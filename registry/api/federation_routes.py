"""
Federation configuration API routes.

Provides endpoints to manage federation configurations.
"""

import asyncio
import copy
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from ..audit import set_audit_action
from ..auth.dependencies import nginx_proxied_auth
from ..repositories.factory import get_federation_config_repository
from ..repositories.interfaces import FederationConfigRepositoryBase
from ..schemas.federation_schema import FederationConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_federation_repo() -> FederationConfigRepositoryBase:
    """Get federation config repository dependency."""
    return get_federation_config_repository()


_VALID_FEDERATION_SOURCES = {"anthropic", "asor"}


def _iso_now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).isoformat()


def _empty_sync_results() -> dict[str, Any]:
    """Build an empty sync result payload."""
    return {"anthropic": {"servers": [], "count": 0}, "asor": {"agents": [], "count": 0}}


ProgressCallback = Callable[[dict[str, Any]], Awaitable[None]]


async def _emit_progress(
    progress_callback: ProgressCallback | None,
    updates: dict[str, Any],
) -> None:
    """Emit a best-effort progress update."""
    if progress_callback is None:
        return

    try:
        await progress_callback(updates)
    except Exception as exc:
        logger.warning(f"Failed to publish federation sync progress update: {exc}")


async def _execute_federation_sync(
    config: FederationConfig,
    source: str | None,
    requested_by: str,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """
    Execute federation sync and return full sync response payload.

    This helper is shared by both blocking and background job execution paths.
    """
    from ..core.nginx_service import nginx_service as nginx_svc
    from ..repositories.factory import get_server_repository
    from ..services.agent_service import agent_service
    from ..services.federation.anthropic_client import AnthropicFederationClient
    from ..services.federation.asor_client import AsorFederationClient
    from ..services.federation_reconciliation import reconcile_anthropic_servers
    from ..services.server_service import server_service

    results = _empty_sync_results()

    await _emit_progress(
        progress_callback,
        {
            "phase": "started",
            "source": source or "all",
            "processed": 0,
            "total": None,
            "synced": 0,
            "errors": 0,
        },
    )

    # Sync Anthropic servers if enabled and requested.
    if (source is None or source == "anthropic") and config.anthropic.enabled:
        logger.info("Syncing servers from Anthropic MCP Registry...")
        anthropic_client = AnthropicFederationClient(endpoint=config.anthropic.endpoint)
        servers = anthropic_client.fetch_all_servers(config.anthropic.servers)
        total_servers = len(servers)
        error_count = 0

        await _emit_progress(
            progress_callback,
            {
                "phase": "syncing_anthropic",
                "source": "anthropic",
                "processed": 0,
                "total": total_servers,
                "synced": 0,
                "errors": error_count,
            },
        )

        for index, server_data in enumerate(servers, start=1):
            try:
                server_path = server_data.get("path")
                if not server_path:
                    logger.warning(f"Server missing path: {server_data.get('server_name')}, skipping")
                    continue

                # server_data already includes a canonical "path".
                register_result = await server_service.register_server(server_data)
                success = register_result["success"]

                if not success and not register_result.get("is_new_version"):
                    logger.warning(f"Server already exists or failed to register: {server_path}")
                    success = await server_service.update_server(server_path, server_data)

                if success:
                    server_name = server_data.get("server_name", server_path)
                    logger.info(
                        f"Synced Anthropic server (disabled by default): {server_name} at {server_path}"
                    )
                    results["anthropic"]["servers"].append(server_name)
                else:
                    error_count += 1
                    logger.error(f"Failed to register or update server: {server_path}")
            except Exception as exc:
                error_count += 1
                logger.error(
                    "Failed to sync Anthropic server "
                    f"{server_data.get('server_name', 'unknown')}: {exc}"
                )

            if index == 1 or index % 10 == 0 or index == total_servers:
                await _emit_progress(
                    progress_callback,
                    {
                        "phase": "syncing_anthropic",
                        "source": "anthropic",
                        "processed": index,
                        "total": total_servers,
                        "synced": len(results["anthropic"]["servers"]),
                        "errors": error_count,
                    },
                )

        results["anthropic"]["count"] = len(results["anthropic"]["servers"])
        logger.info(f"Synced {results['anthropic']['count']} servers from Anthropic")

    # Sync ASOR agents if enabled and requested.
    if (source is None or source == "asor") and config.asor.enabled:
        logger.info("Syncing agents from ASOR...")
        from ..schemas.agent_models import AgentCard

        tenant_url = (
            config.asor.endpoint.split("/api")[0]
            if "/api" in config.asor.endpoint
            else config.asor.endpoint
        )
        asor_client = AsorFederationClient(
            endpoint=config.asor.endpoint,
            auth_env_var=config.asor.auth_env_var,
            tenant_url=tenant_url,
        )
        agents = asor_client.fetch_all_agents(config.asor.agents)
        total_agents = len(agents)
        error_count = 0

        await _emit_progress(
            progress_callback,
            {
                "phase": "syncing_asor",
                "source": "asor",
                "processed": 0,
                "total": total_agents,
                "synced": 0,
                "errors": error_count,
            },
        )

        for index, agent_data in enumerate(agents, start=1):
            try:
                agent_name = agent_data.get("name", "Unknown ASOR Agent")
                agent_path = f"/{agent_name.lower().replace('_', '-')}"

                skills = []
                for skill in agent_data.get("skills", []):
                    skills.append(
                        {
                            "name": skill.get("name", ""),
                            "description": skill.get("description", ""),
                            "id": skill.get("id", ""),
                        }
                    )

                agent_card = AgentCard(
                    protocol_version="1.0",
                    name=agent_name,
                    path=agent_path,
                    url=agent_data.get("url", ""),
                    description=agent_data.get("description", f"ASOR agent: {agent_name}"),
                    version=agent_data.get("version", "1.0.0"),
                    provider="ASOR",
                    author="ASOR",
                    license="Unknown",
                    skills=skills,
                    tags=["asor", "federated", "workday"],
                    visibility="public",
                    registered_by="asor-federation",
                    registered_at=datetime.now(UTC),
                )

                if agent_path not in agent_service.registered_agents:
                    await agent_service.register_agent(agent_card)
                    logger.info(f"Synced ASOR agent: {agent_name}")
                    results["asor"]["agents"].append(agent_name)
            except Exception as exc:
                error_count += 1
                logger.error(
                    f"Failed to sync ASOR agent {agent_data.get('name', 'unknown')}: {exc}"
                )

            if index == 1 or index % 10 == 0 or index == total_agents:
                await _emit_progress(
                    progress_callback,
                    {
                        "phase": "syncing_asor",
                        "source": "asor",
                        "processed": index,
                        "total": total_agents,
                        "synced": len(results["asor"]["agents"]),
                        "errors": error_count,
                    },
                )

        results["asor"]["count"] = len(results["asor"]["agents"])
        logger.info(f"Synced {results['asor']['count']} agents from ASOR")

    reconciliation_result = None
    try:
        server_repo = get_server_repository()
        reconciliation_result = await reconcile_anthropic_servers(
            config=config,
            server_service=server_service,
            server_repo=server_repo,
            nginx_service=nginx_svc,
            audit_username=requested_by,
        )
        if reconciliation_result.get("removed"):
            logger.info(
                f"Reconciliation removed {reconciliation_result['removed_count']} stale servers: "
                f"{reconciliation_result['removed']}"
            )
    except Exception as reconcile_error:
        logger.warning(f"Reconciliation failed after sync: {reconcile_error}")

    total_synced = results["anthropic"]["count"] + results["asor"]["count"]
    await _emit_progress(
        progress_callback,
        {
            "phase": "completed",
            "source": source or "all",
            "processed": total_synced,
            "total": total_synced,
            "synced": total_synced,
            "errors": 0,
        },
    )

    return {
        "results": results,
        "total_synced": total_synced,
        "reconciliation": reconciliation_result,
    }


class FederationSyncJobManager:
    """In-memory coordinator for detached federation sync jobs."""

    def __init__(self, max_history: int = 30):
        self._jobs: dict[str, dict[str, Any]] = {}
        self._order: list[str] = []
        self._tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._max_history = max_history

    async def create_job(
        self,
        config_id: str,
        source: str | None,
        requested_by: str,
        config: FederationConfig,
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Create and start a federation sync job unless another is active."""
        async with self._lock:
            active_job_id = self._get_active_job_id_locked()
            if active_job_id:
                return None, active_job_id

            job_id = uuid4().hex
            now_iso = _iso_now()
            job = {
                "job_id": job_id,
                "config_id": config_id,
                "source": source or "all",
                "requested_by": requested_by,
                "status": "queued",
                "created_at": now_iso,
                "started_at": None,
                "completed_at": None,
                "error": None,
                "result": None,
                "progress": {
                    "phase": "queued",
                    "source": source or "all",
                    "processed": 0,
                    "total": None,
                    "synced": 0,
                    "errors": 0,
                    "updated_at": now_iso,
                },
            }
            self._jobs[job_id] = job
            self._order.append(job_id)
            self._prune_locked()

            task = asyncio.create_task(self._run_job(job_id=job_id, config=config, source=source))
            self._tasks[job_id] = task
            return copy.deepcopy(job), None

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get a job by id."""
        async with self._lock:
            job = self._jobs.get(job_id)
            return copy.deepcopy(job) if job else None

    async def list_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        """List jobs in descending recency order."""
        async with self._lock:
            ordered = list(reversed(self._order))[:limit]
            return [copy.deepcopy(self._jobs[job_id]) for job_id in ordered if job_id in self._jobs]

    async def _run_job(self, job_id: str, config: FederationConfig, source: str | None) -> None:
        """Execute a queued sync job."""
        await self._update_job(
            job_id,
            {
                "status": "running",
                "started_at": _iso_now(),
                "progress": {"phase": "running"},
            },
        )

        try:
            requested_by = await self._get_requested_by(job_id)
            sync_response = await _execute_federation_sync(
                config=config,
                source=source,
                requested_by=requested_by,
                progress_callback=lambda updates: self._update_job(
                    job_id,
                    {"progress": updates},
                ),
            )

            await self._update_job(
                job_id,
                {
                    "status": "completed",
                    "completed_at": _iso_now(),
                    "result": {
                        "total_synced": sync_response["total_synced"],
                        "results": {
                            "anthropic": {"count": sync_response["results"]["anthropic"]["count"]},
                            "asor": {"count": sync_response["results"]["asor"]["count"]},
                        },
                        "reconciliation": sync_response.get("reconciliation"),
                    },
                    "progress": {"phase": "completed"},
                },
            )
        except Exception as exc:
            logger.error(f"Federation background sync job failed: {exc}", exc_info=True)
            await self._update_job(
                job_id,
                {
                    "status": "failed",
                    "completed_at": _iso_now(),
                    "error": str(exc),
                    "progress": {"phase": "failed"},
                },
            )
        finally:
            async with self._lock:
                self._tasks.pop(job_id, None)

    async def _get_requested_by(self, job_id: str) -> str:
        """Read requesting user for a job."""
        async with self._lock:
            job = self._jobs.get(job_id) or {}
            return str(job.get("requested_by") or "unknown")

    async def _update_job(self, job_id: str, updates: dict[str, Any]) -> None:
        """Apply partial updates to a job entry."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return

            progress_updates = updates.pop("progress", None)
            for key, value in updates.items():
                job[key] = value

            if progress_updates:
                progress = job.setdefault("progress", {})
                progress.update(progress_updates)
                progress["updated_at"] = _iso_now()

    def _get_active_job_id_locked(self) -> str | None:
        for job_id in reversed(self._order):
            job = self._jobs.get(job_id, {})
            if job.get("status") in {"queued", "running"}:
                return job_id
        return None

    def _prune_locked(self) -> None:
        """Keep completed history bounded while preserving active jobs."""
        while len(self._order) > self._max_history:
            removable_id = None
            for candidate in self._order:
                candidate_status = self._jobs.get(candidate, {}).get("status")
                if candidate_status not in {"queued", "running"}:
                    removable_id = candidate
                    break

            if removable_id is None:
                return

            self._order.remove(removable_id)
            self._jobs.pop(removable_id, None)


_federation_sync_job_manager = FederationSyncJobManager()


@router.get("/federation/config", tags=["federation"], summary="Get federation configuration")
async def get_federation_config(
    request: Request,
    config_id: str = "default",
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Get federation configuration by ID.

    Args:
        config_id: Configuration ID (default: "default")
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Federation configuration

    Raises:
        404: Configuration not found
    """
    # Set audit action for federation config read
    set_audit_action(
        request,
        "read",
        "federation",
        resource_id=config_id,
        description=f"Read federation config {config_id}",
    )

    logger.info(f"User {user_context['username']} retrieving federation config: {config_id}")

    config = await repo.get_config(config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    return config.model_dump()


@router.post(
    "/federation/config",
    tags=["federation"],
    summary="Create or update federation configuration",
    status_code=status.HTTP_201_CREATED,
)
async def save_federation_config(
    request: Request,
    config: FederationConfig,
    config_id: str = "default",
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Create or update federation configuration.

    Args:
        config: Federation configuration to save
        config_id: Configuration ID (default: "default")
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Saved configuration

    Example:
        ```json
        {
          "anthropic": {
            "enabled": true,
            "endpoint": "https://registry.modelcontextprotocol.io",
            "sync_on_startup": false,
            "servers": [
              {"name": "io.github.jgador/websharp"},
              {"name": "modelcontextprotocol/filesystem"}
            ]
          },
          "asor": {
            "enabled": false,
            "endpoint": "",
            "auth_env_var": "ASOR_ACCESS_TOKEN",
            "sync_on_startup": false,
            "agents": []
          }
        }
        ```
    """
    # Set audit action for federation config create/update
    set_audit_action(
        request,
        "create",
        "federation",
        resource_id=config_id,
        description=f"Save federation config {config_id}",
    )

    logger.info(
        f"User {user_context['username']} saving federation config: {config_id} "
        f"(anthropic: {config.anthropic.enabled}, asor: {config.asor.enabled})"
    )

    try:
        saved_config = await repo.save_config(config, config_id)
        logger.info(f"Federation config saved successfully: {config_id}")

        # Reconcile: remove stale federated servers
        reconciliation_result = None
        try:
            from ..core.nginx_service import nginx_service
            from ..repositories.factory import get_server_repository
            from ..services.federation_reconciliation import reconcile_anthropic_servers
            from ..services.server_service import server_service

            server_repo = get_server_repository()
            reconciliation_result = await reconcile_anthropic_servers(
                config=saved_config,
                server_service=server_service,
                server_repo=server_repo,
                nginx_service=nginx_service,
                audit_username=user_context.get("username"),
            )
            if reconciliation_result.get("removed"):
                logger.info(
                    f"Reconciliation removed {reconciliation_result['removed_count']} stale servers: "
                    f"{reconciliation_result['removed']}"
                )
        except Exception as e:
            logger.error(f"Reconciliation failed (non-fatal): {e}")

        response = {
            "message": "Federation configuration saved successfully",
            "config_id": config_id,
            "config": saved_config.model_dump(),
        }
        if reconciliation_result:
            response["reconciliation"] = reconciliation_result

        return response

    except Exception as e:
        logger.error(f"Failed to save federation config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save federation config: {str(e)}",
        )


@router.put(
    "/federation/config/{config_id}",
    tags=["federation"],
    summary="Update specific federation configuration",
)
async def update_federation_config(
    request: Request,
    config_id: str,
    config: FederationConfig,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Update a specific federation configuration.

    Args:
        config_id: Configuration ID to update
        config: Updated federation configuration
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Updated configuration
    """
    # Set audit action for federation config update
    set_audit_action(
        request,
        "update",
        "federation",
        resource_id=config_id,
        description=f"Update federation config {config_id}",
    )

    logger.info(f"User {user_context['username']} updating federation config: {config_id}")

    try:
        saved_config = await repo.save_config(config, config_id)
        logger.info(f"Federation config updated successfully: {config_id}")

        # Reconcile: remove stale federated servers
        reconciliation_result = None
        try:
            from ..core.nginx_service import nginx_service
            from ..repositories.factory import get_server_repository
            from ..services.federation_reconciliation import reconcile_anthropic_servers
            from ..services.server_service import server_service

            server_repo = get_server_repository()
            reconciliation_result = await reconcile_anthropic_servers(
                config=saved_config,
                server_service=server_service,
                server_repo=server_repo,
                nginx_service=nginx_service,
                audit_username=user_context.get("username"),
            )
            if reconciliation_result.get("removed"):
                logger.info(
                    f"Reconciliation removed {reconciliation_result['removed_count']} stale servers: "
                    f"{reconciliation_result['removed']}"
                )
        except Exception as e:
            logger.error(f"Reconciliation failed (non-fatal): {e}")

        response = {
            "message": "Federation configuration updated successfully",
            "config_id": config_id,
            "config": saved_config.model_dump(),
        }
        if reconciliation_result:
            response["reconciliation"] = reconciliation_result

        return response

    except Exception as e:
        logger.error(f"Failed to update federation config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update federation config: {str(e)}",
        )


@router.delete(
    "/federation/config/{config_id}", tags=["federation"], summary="Delete federation configuration"
)
async def delete_federation_config(
    config_id: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, str]:
    """
    Delete a federation configuration.

    Args:
        config_id: Configuration ID to delete
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Deletion confirmation

    Raises:
        404: Configuration not found
    """
    logger.info(f"User {user_context['username']} deleting federation config: {config_id}")

    deleted = await repo.delete_config(config_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    logger.info(f"Federation config deleted successfully: {config_id}")
    return {
        "message": f"Federation configuration '{config_id}' deleted successfully",
        "config_id": config_id,
    }


@router.get(
    "/federation/configs", tags=["federation"], summary="List all federation configurations"
)
async def list_federation_configs(
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    List all federation configurations.

    Args:
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        List of configuration summaries with id, created_at, updated_at
    """
    logger.info(f"User {user_context['username']} listing federation configs")

    configs = await repo.list_configs()

    return {"configs": configs, "total": len(configs)}


@router.post(
    "/federation/config/{config_id}/anthropic/servers",
    tags=["federation"],
    summary="Add Anthropic server to config",
)
async def add_anthropic_server(
    config_id: str,
    server_name: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Add a server to Anthropic federation configuration.

    Args:
        config_id: Configuration ID
        server_name: Server name to add (e.g., "io.github.jgador/websharp")
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Updated configuration
    """
    logger.info(f"User {user_context['username']} adding Anthropic server: {server_name}")

    config = await repo.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    # Check if server already exists
    from ..schemas.federation_schema import AnthropicServerConfig

    for server in config.anthropic.servers:
        if server.name == server_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Server '{server_name}' already exists in configuration",
            )

    # Add new server
    config.anthropic.servers.append(AnthropicServerConfig(name=server_name))

    # Save updated config
    saved_config = await repo.save_config(config, config_id)

    return {
        "message": f"Server '{server_name}' added to Anthropic configuration",
        "config": saved_config.model_dump(),
    }


@router.delete(
    "/federation/config/{config_id}/anthropic/servers/{server_name:path}",
    tags=["federation"],
    summary="Remove Anthropic server from config",
)
async def remove_anthropic_server(
    config_id: str,
    server_name: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Remove a server from Anthropic federation configuration.

    Also removes the server from mcp_servers_default if it was
    previously synced.

    Args:
        config_id: Configuration ID
        server_name: Server name to remove (e.g., "io.github.jgador/websharp")
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Updated configuration with removal details
    """
    logger.info(f"User {user_context['username']} removing Anthropic server: {server_name}")

    config = await repo.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    # Find and remove server from config
    original_count = len(config.anthropic.servers)
    config.anthropic.servers = [s for s in config.anthropic.servers if s.name != server_name]

    if len(config.anthropic.servers) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server '{server_name}' not found in configuration",
        )

    # Save updated config
    saved_config = await repo.save_config(config, config_id)

    # Remove the server from mcp_servers_default if it exists
    server_path = f"/{server_name.replace('/', '-')}"
    server_removed = False
    try:
        from ..services.server_service import server_service

        server_info = await server_service.get_server_info(server_path)
        if server_info and server_info.get("source") == "anthropic":
            server_removed = await server_service.remove_server(server_path)
            if server_removed:
                logger.info(f"Removed server '{server_name}' from mcp_servers_default ({server_path})")

                # Regenerate nginx config
                from ..core.nginx_service import nginx_service

                all_servers = await server_service.get_all_servers(
                    include_inactive=False,
                )
                enabled_servers = {
                    p: info
                    for p, info in all_servers.items()
                    if info.get("is_enabled", False)
                }
                await nginx_service.generate_config_async(enabled_servers)
    except Exception as e:
        logger.error(f"Failed to remove server from mcp_servers_default: {e}")

    return {
        "message": f"Server '{server_name}' removed from Anthropic configuration",
        "config": saved_config.model_dump(),
        "server_removed_from_registry": server_removed,
    }


@router.post(
    "/federation/config/{config_id}/asor/agents",
    tags=["federation"],
    summary="Add ASOR agent to config",
)
async def add_asor_agent(
    config_id: str,
    agent_id: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Add an agent to ASOR federation configuration.

    Args:
        config_id: Configuration ID
        agent_id: Agent ID to add (e.g., "aws_assistant")
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Updated configuration
    """
    logger.info(f"User {user_context['username']} adding ASOR agent: {agent_id}")

    config = await repo.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    # Check if agent already exists
    from ..schemas.federation_schema import AsorAgentConfig

    for agent in config.asor.agents:
        if agent.id == agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent '{agent_id}' already exists in configuration",
            )

    # Add new agent
    config.asor.agents.append(AsorAgentConfig(id=agent_id))

    # Save updated config
    saved_config = await repo.save_config(config, config_id)

    return {
        "message": f"Agent '{agent_id}' added to ASOR configuration",
        "config": saved_config.model_dump(),
    }


@router.delete(
    "/federation/config/{config_id}/asor/agents/{agent_id}",
    tags=["federation"],
    summary="Remove ASOR agent from config",
)
async def remove_asor_agent(
    config_id: str,
    agent_id: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Remove an agent from ASOR federation configuration.

    Args:
        config_id: Configuration ID
        agent_id: Agent ID to remove
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Updated configuration
    """
    logger.info(f"User {user_context['username']} removing ASOR agent: {agent_id}")

    config = await repo.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    # Find and remove agent
    original_count = len(config.asor.agents)
    config.asor.agents = [a for a in config.asor.agents if a.id != agent_id]

    if len(config.asor.agents) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found in configuration",
        )

    # Save updated config
    saved_config = await repo.save_config(config, config_id)

    return {
        "message": f"Agent '{agent_id}' removed from ASOR configuration",
        "config": saved_config.model_dump(),
    }


@router.post("/federation/sync", tags=["federation"], summary="Trigger manual federation sync")
async def sync_federation(
    request: Request,
    config_id: str = "default",
    source: str | None = None,
    background: bool = True,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
    repo: FederationConfigRepositoryBase = Depends(_get_federation_repo),
) -> dict[str, Any]:
    """
    Manually trigger federation sync to import servers/agents from configured sources.

    Args:
        config_id: Configuration ID to use for sync (default: "default")
        source: Optional source filter ("anthropic" or "asor"). If None, syncs all enabled sources.
        background: Run as detached job (default: true). Set false for blocking behavior.
        user_context: Authenticated user context
        repo: Federation config repository

    Returns:
        Job metadata when background=true (default) or sync results when background=false.

    Example:
        Queue background sync (default):
        ```bash
        POST /api/federation/sync
        ```

        Queue background sync for Anthropic only:
        ```bash
        POST /api/federation/sync?source=anthropic
        ```

        Run blocking sync:
        ```bash
        POST /api/federation/sync?background=false
        ```
    """
    if source is not None and source not in _VALID_FEDERATION_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source '{source}'. Expected one of: anthropic, asor",
        )

    # Set audit action for federation sync
    set_audit_action(
        request,
        "sync",
        "federation",
        resource_id=config_id,
        description=f"Sync federation from {source or 'all sources'}",
    )

    username = user_context["username"]
    logger.info(
        f"User {username} triggering federation sync: {config_id} "
        f"(source={source or 'all'}, background={background})"
    )

    # Get federation config
    config = await repo.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation config '{config_id}' not found",
        )

    if background:
        job, active_job_id = await _federation_sync_job_manager.create_job(
            config_id=config_id,
            source=source,
            requested_by=username,
            config=config,
        )

        if active_job_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A federation sync job is already running. "
                    f"Active job id: {active_job_id}"
                ),
            )

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": "Federation sync queued",
                "config_id": config_id,
                "job_id": job["job_id"],
                "job": job,
                "status_endpoint": f"/api/federation/sync/jobs/{job['job_id']}",
            },
        )

    try:
        sync_response = await _execute_federation_sync(
            config=config,
            source=source,
            requested_by=username,
        )
        return {
            "message": "Federation sync completed",
            "config_id": config_id,
            "results": sync_response["results"],
            "total_synced": sync_response["total_synced"],
            "reconciliation": sync_response.get("reconciliation"),
        }
    except Exception as exc:
        logger.error(f"Federation sync failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Federation sync failed: {str(exc)}",
        )


@router.get(
    "/federation/sync/jobs",
    tags=["federation"],
    summary="List federation sync jobs",
)
async def list_federation_sync_jobs(
    limit: int = Query(default=20, ge=1, le=200),
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
) -> dict[str, Any]:
    """List recent federation sync jobs with current status and progress."""
    logger.info(f"User {user_context['username']} listing federation sync jobs")
    jobs = await _federation_sync_job_manager.list_jobs(limit=limit)

    active_job_id = None
    for job in jobs:
        if job.get("status") in {"queued", "running"}:
            active_job_id = job.get("job_id")
            break

    return {
        "jobs": jobs,
        "total": len(jobs),
        "active_job_id": active_job_id,
    }


@router.get(
    "/federation/sync/jobs/{job_id}",
    tags=["federation"],
    summary="Get federation sync job status",
)
async def get_federation_sync_job(
    job_id: str,
    user_context: Annotated[dict, Depends(nginx_proxied_auth)] = None,
) -> dict[str, Any]:
    """Get detailed status for a single federation sync job."""
    logger.info(f"User {user_context['username']} retrieving federation sync job: {job_id}")
    job = await _federation_sync_job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Federation sync job '{job_id}' not found",
        )
    return job
