# AGENTS Instructions (Production Branch)

This file defines coding-agent operating rules for this repository's `production` branch.

If any summary below conflicts with upstream source docs, upstream source docs win:
- `CONTRIBUTING.md`
- `DEV_INSTRUCTIONS.md`
- `docs/llms.txt`
- `CLAUDE.md`

## Scope and Branch Model

- Upstream source of truth: `agentic-community/mcp-gateway-registry`.
- Fork: `joshphillipssr/joshsr-ai-unified-agentic-integration-platform`.
- `main` branch policy: mirror upstream `main` as closely as possible.
- `production` branch policy: fork-specific operational/customization layer (including UAIP branding and deployment differences).

## Required Read Order (Before Substantive Changes)

1. `CONTRIBUTING.md`
2. `DEV_INSTRUCTIONS.md`
3. `docs/llms.txt`
4. `CLAUDE.md`

## Upstream Contribution Requirements (Synthesized)

- Base upstream contribution work on the latest `main`.
- Keep pull requests focused to one change set.
- Open an issue first for significant work.
- Run local tests and submit only passing changes.
- Use clear, professional commit messages.
- Stay engaged with CI failures and review feedback.
- Report security vulnerabilities privately via AWS vulnerability reporting; do not open public security issues.

## Coding and Architecture Conventions

- Use `uv` + `pyproject.toml` for Python dependency/runtime workflows.
- Follow modern typing conventions (PEP 604/585): `X | None`, built-in generics (`list`, `dict`, etc.).
- Preserve architecture boundaries from `docs/llms.txt`:
  - `API Routes -> Services -> Repositories -> Storage Backends`
  - No direct repository access from API routes.
  - Service layer must obtain repositories via factory pattern.
  - Keep code backend-agnostic (no hardcoded backend assumptions).
- Treat file-based repository backend as legacy/deprecated; prefer MongoDB/DocumentDB paths for active work.
- Security hygiene:
  - Never commit secrets or `.env` values.
  - Validate external input.
  - For subprocess usage: list-form commands, no `shell=True`, always timeout and error handling.
  - For SQL: parameterized queries and allowlist validation for identifiers.
- Documentation and PR hygiene:
  - Keep commit/PR text professional (no AI attribution footer text).
  - Keep README/docs style professional and consistent with upstream conventions.

## Validation Checklist

Run before submitting changes:

1. Generate fresh credentials:
   - `./credentials-provider/generate_creds.sh`
2. Fast local suite:
   - `./tests/run_all_tests.sh --skip-production`
3. Merge-ready full suite (required for PR merge):
   - `./tests/run_all_tests.sh`
4. Run configured lint/type/security checks from project tooling (`pre-commit`, `ruff`, `mypy`, `bandit`) as applicable.

When a change is deployed to a live environment (for example neo), run this smoke checklist before handoff:

1. Service health:
   - `docker compose -f docker-compose.yml -f docker-compose.neo.yml ps` shows `healthy` (or `Up` where no healthcheck exists) for `registry`, `auth-server`, and `mcpgw-server`.
2. Host routing:
   - `https://registry.mcp.joshsr.ai/` returns HTTP `200`.
   - `https://keycloak.mcp.joshsr.ai/` returns redirect/login (`302` or `200` depending on client follow behavior).
3. OAuth/Gateway guardrail checks:
   - `https://mcp.joshsr.ai/mcp/agentic` returns `401` when called without auth.
   - `https://mcp.joshsr.ai/mcp/docker` returns `401` when called without auth.
4. Regression scan:
   - `docker compose ... logs --tail 120 registry auth-server mcpgw-server` has no startup crash loops (`ModuleNotFoundError`, repeated restarts).

## Fork Customization Workflow

- Track fork-only divergence in `customizations.md`.
- Every non-upstream change must add or update a `customizations.md` entry.
- Do not open upstream PRs from `production`.
- For upstream PRs:
  - Branch from `main`.
  - Include only upstream-eligible changes.
  - Exclude fork-only branding, infra, or environment-specific customizations.
- After upstream sync/merge operations, reconcile `customizations.md` status for affected entries.

## Reference Index

- Contribution policy: `CONTRIBUTING.md`
- Contributor workflow and required test commands: `DEV_INSTRUCTIONS.md`
- Architecture and platform behavior: `docs/llms.txt`
- Coding and security standards: `CLAUDE.md`
- Fork divergence ledger: `customizations.md`
