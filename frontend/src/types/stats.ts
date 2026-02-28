/**
 * Shared system statistics type definitions for the MCP Gateway Registry frontend.
 *
 * These interfaces mirror the backend Pydantic models defined in
 * registry/api/stats.py.
 */


/**
 * Database health status.
 *
 * Indicates whether the database connection is healthy and operational.
 */
export interface DatabaseStatus {
  status: string;
  message: string;
}


/**
 * System-level statistics.
 *
 * Provides platform information, Python version, and system resource details.
 */
export interface SystemStats {
  hostname: string;
  platform: string;
  deployment_type: string;
  python_version: string;
  uptime_seconds: number;
  pid: number;
}


/**
 * Complete registry statistics response.
 *
 * Contains uptime, registry counts, and system information.
 */
export interface RegistryStats {
  uptime_seconds: number;
  registry_stats: {
    total_servers: number;
    enabled_servers: number;
    total_agents: number;
    enabled_agents: number;
    total_skills: number;
    total_virtual_servers: number;
    enabled_virtual_servers: number;
  };
  database_status: DatabaseStatus;
  system_stats: SystemStats;
}
