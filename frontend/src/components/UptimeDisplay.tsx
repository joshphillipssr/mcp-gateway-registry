import React, {
  useState,
  useEffect,
} from 'react';
import {
  RegistryStats,
} from '../types/stats';


/**
 * UptimeDisplay component shows system uptime with a hover tooltip containing detailed stats.
 *
 * Features:
 * - Fetches /api/stats every 60 seconds
 * - Displays human-readable uptime (e.g., "1d 2h 34m")
 * - Shows detailed system info on hover
 * - Handles loading and error states gracefully
 * - Hidden on mobile screens (<768px)
 */
const UptimeDisplay: React.FC = () => {
  const [stats, setStats] = useState<RegistryStats | null>(null);
  const [error, setError] = useState<boolean>(false);


  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
          throw new Error('Failed to fetch stats');
        }
        const data = await response.json();
        setStats(data);
        setError(false);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(true);
      }
    };

    // Initial fetch
    fetchStats();

    // Poll every 60 seconds
    const interval = setInterval(fetchStats, 60000);

    return () => clearInterval(interval);
  }, []);


  const formatUptime = (
    seconds: number,
  ): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    const parts: string[] = [];
    if (days > 0) {
      parts.push(`${days}d`);
    }
    if (hours > 0) {
      parts.push(`${hours}h`);
    }
    if (minutes > 0 || parts.length === 0) {
      parts.push(`${minutes}m`);
    }

    return parts.join(' ');
  };


  if (error) {
    return (
      <div className="hidden md:flex items-center px-2.5 py-1 bg-gray-50 dark:bg-gray-900/20 rounded-md">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
          Uptime: unavailable
        </span>
      </div>
    );
  }


  if (!stats) {
    return null;
  }


  const uptimeText = formatUptime(stats.uptime_seconds);
  const dbStatusColor = stats.database_status.status === 'healthy'
    ? 'text-green-600 dark:text-green-400'
    : 'text-red-600 dark:text-red-400';


  return (
    <div className="hidden md:flex items-center px-2.5 py-1 bg-green-50 dark:bg-green-900/20 rounded-md group relative">
      <span className="text-xs font-medium text-green-700 dark:text-green-300">
        Uptime: {uptimeText}
      </span>

      {/* Tooltip on hover */}
      <div className="absolute right-0 top-full mt-2 w-80 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 p-4">
          {/* System Info */}
          <div className="mb-3">
            <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
              System Information
            </h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Hostname:</span>
                <span className="text-gray-900 dark:text-gray-100 font-mono">
                  {stats.system_stats.hostname}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Platform:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.system_stats.platform}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Deployment:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.system_stats.deployment_type}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Python:</span>
                <span className="text-gray-900 dark:text-gray-100 font-mono">
                  {stats.system_stats.python_version}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">PID:</span>
                <span className="text-gray-900 dark:text-gray-100 font-mono">
                  {stats.system_stats.pid}
                </span>
              </div>
            </div>
          </div>

          {/* Registry Stats */}
          <div className="mb-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Registry Statistics
            </h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Servers:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.registry_stats.enabled_servers} / {stats.registry_stats.total_servers}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Agents:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.registry_stats.enabled_agents} / {stats.registry_stats.total_agents}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Skills:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.registry_stats.total_skills}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Virtual Servers:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {stats.registry_stats.enabled_virtual_servers} / {stats.registry_stats.total_virtual_servers}
                </span>
              </div>
            </div>
          </div>

          {/* Database Status */}
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Database Status
            </h3>
            <div className="text-xs">
              <div className="flex justify-between items-center">
                <span className="text-gray-500 dark:text-gray-400">Status:</span>
                <span className={`font-semibold ${dbStatusColor}`}>
                  {stats.database_status.status}
                </span>
              </div>
              {stats.database_status.message && (
                <div className="mt-1 text-gray-600 dark:text-gray-400 text-xs">
                  {stats.database_status.message}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


export default UptimeDisplay;
