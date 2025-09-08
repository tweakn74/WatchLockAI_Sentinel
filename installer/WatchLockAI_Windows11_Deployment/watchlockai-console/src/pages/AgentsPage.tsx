import React from 'react';
import { useAuth } from '../lib/auth';
import { useAgents } from '../hooks/useSupabaseQuery';
import { Monitor, Users, Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { DataTable } from '../components/ui/DataTable';
import { StatusIndicator } from '../components/ui/StatusIndicator';
import { formatTimeAgo } from '../lib/utils';

export function AgentsPage() {
  const { profile } = useAuth();
  const organizationId = profile?.organization_id;
  const { data: agentsData, isLoading } = useAgents(organizationId || '');

  const agents = agentsData?.agents || [];
  const metrics = agentsData?.metrics || { total: 0, online: 0, offline: 0, unhealthy: 0 };

  const agentColumns = [
    {
      key: 'hostname' as string,
      label: 'Hostname',
      render: (value: string) => (
        <span className="font-medium text-gray-900">{value}</span>
      )
    },
    {
      key: 'os_type' as string,
      label: 'OS Type'
    },
    {
      key: 'status' as string,
      label: 'Status',
      render: (value: string) => (
        <StatusIndicator status={value === 'online' ? 'online' : 'offline'} size="sm" />
      )
    },
    {
      key: 'last_heartbeat' as string,
      label: 'Last Seen',
      render: (value: string) => value ? formatTimeAgo(value) : 'Never'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Agent Fleet Management</h1>
        <p className="text-gray-600 mt-1">
          Monitor and manage WatchLockAI agents across your infrastructure
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Agents"
          value={metrics.total}
          icon={<Monitor className="w-6 h-6" />}
          color="blue"
        />
        <MetricCard
          title="Online Agents"
          value={metrics.online}
          icon={<Wifi className="w-6 h-6" />}
          color="green"
        />
        <MetricCard
          title="Offline Agents"
          value={metrics.offline}
          icon={<WifiOff className="w-6 h-6" />}
          color="red"
        />
        <MetricCard
          title="Health Issues"
          value={metrics.unhealthy}
          icon={<AlertTriangle className="w-6 h-6" />}
          color="yellow"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Endpoint Agents</CardTitle>
        </CardHeader>
        <CardContent padding="none">
          <DataTable
            data={agents}
            columns={agentColumns}
            loading={isLoading}
            emptyMessage="No agents registered"
          />
        </CardContent>
      </Card>
    </div>
  );
}