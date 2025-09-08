import React from 'react';
import { useAuth } from '../lib/auth';
import { useDashboardMetrics, useThreats, useAgents } from '../hooks/useApiData';
import { 
  Shield, 
  Monitor, 
  AlertTriangle, 
  Activity,
  TrendingUp,
  Users,
  Zap,
  Clock
} from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { ChartContainer } from '../components/ui/ChartContainer';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/badge';
import { StatusIndicator } from '../components/ui/StatusIndicator';
import { FilterTabs } from '../components/ui/FilterTabs';
import { formatTimeAgo, getSeverityColor, getStatusColor } from '../lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const SEVERITY_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6'
};

export function DashboardPage() {
  const { profile } = useAuth();
  const organizationId = profile?.organization_id;
  
  const { metrics, threats, agents, loading: metricsLoading } = useDashboardMetrics(organizationId);
  const { data: threatsData, loading: threatsLoading } = useThreats(organizationId);
  const { data: agentsData, loading: agentsLoading } = useAgents(organizationId);

  const threatsList = threats || [];
  const agentsList = agents || [];
  const agentMetrics = { total: (agentsList || []).length, online: (agentsList || []).filter(a => a.status === 'online').length, offline: (agentsList || []).filter(a => a.status === 'offline').length, unhealthy: (agentsList || []).filter(a => a.status === 'error').length };

  // Sample data for charts (in production, this would come from the metrics API)
  const threatTrendData = [
    { time: '00:00', threats: 12 },
    { time: '04:00', threats: 8 },
    { time: '08:00', threats: 15 },
    { time: '12:00', threats: 23 },
    { time: '16:00', threats: 18 },
    { time: '20:00', threats: 14 }
  ];

  const severityData = [
    { name: 'Critical', value: (threatsList || []).filter(t => t.severity === 'critical').length, fill: SEVERITY_COLORS.critical },
    { name: 'High', value: (threatsList || []).filter(t => t.severity === 'high').length, fill: SEVERITY_COLORS.high },
    { name: 'Medium', value: (threatsList || []).filter(t => t.severity === 'medium').length, fill: SEVERITY_COLORS.medium },
    { name: 'Low', value: (threatsList || []).filter(t => t.severity === 'low').length, fill: SEVERITY_COLORS.low }
  ];

  const threatColumns = [
    {
      key: 'severity' as string,
      label: 'Severity',
      render: (value: string) => (
        <Badge className={getSeverityColor(value)}>
          {value.toUpperCase()}
        </Badge>
      )
    },
    {
      key: 'title' as string,
      label: 'Threat',
      render: (value: string) => (
        <span className="font-medium text-gray-900">{value}</span>
      )
    },
    {
      key: 'threat_type' as string,
      label: 'Type'
    },
    {
      key: 'first_seen' as string,
      label: 'First Seen',
      render: (value: string) => formatTimeAgo(value)
    },
    {
      key: 'status' as string,
      label: 'Status',
      render: (value: string) => {
        // Map threat status to StatusIndicator status
        const statusMap: { [key: string]: 'online' | 'offline' | 'warning' | 'error' | 'success' | 'pending' } = {
          'open': 'error',
          'investigating': 'warning', 
          'resolved': 'success',
          'closed': 'success'
        };
        return (
          <StatusIndicator 
            status={statusMap[value] || 'pending'} 
            size="sm"
          />
        );
      }
    }
  ];

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
      label: 'OS'
    },
    {
      key: 'status' as string,
      label: 'Status',
      render: (value: string) => (
        <StatusIndicator 
          status={value === 'online' ? 'online' : 'offline'} 
          size="sm"
        />
      )
    },
    {
      key: 'last_heartbeat' as string,
      label: 'Last Seen',
      render: (value: string) => value ? formatTimeAgo(value) : 'Never'
    },
    {
      key: 'cpu_usage' as string,
      label: 'CPU',
      render: (value: number) => value ? `${value}%` : 'N/A'
    }
  ];

  if (metricsLoading || threatsLoading || agentsLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome back, {profile?.full_name || 'Security Analyst'}
        </h1>
        <p className="text-blue-100">
          Your security operations center is monitoring {agents.length} endpoints with {threats.length} active threats requiring attention.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Threats"
          value={threats.length}
          icon={<Shield className="w-6 h-6" />}
          color="red"
          change={{
            value: 12,
            period: 'vs last 24h',
            isPositive: false
          }}
        />
        
        <MetricCard
          title="Online Agents"
          value={agentMetrics.online}
          icon={<Monitor className="w-6 h-6" />}
          color="green"
          change={{
            value: 5,
            period: 'vs last hour',
            isPositive: true
          }}
        />
        
        <MetricCard
          title="Critical Incidents"
          value={(threatsList || []).filter(t => t.severity === 'critical').length}
          icon={<AlertTriangle className="w-6 h-6" />}
          color="red"
        />
        
        <MetricCard
          title="Response Time"
          value="4.2m"
          icon={<Clock className="w-6 h-6" />}
          color="blue"
          change={{
            value: 8,
            period: 'improvement',
            isPositive: true
          }}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Trends */}
        <ChartContainer 
          title="Threat Activity (24h)"
          subtitle="Real-time threat detection over the last 24 hours"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={threatTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="threats" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={{ fill: '#ef4444' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>

        {/* Severity Distribution */}
        <ChartContainer 
          title="Threat Severity Distribution"
          subtitle="Breakdown of threats by severity level"
        >
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {severityData.map((entry, index) => (
                  <Cell key={index} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

      {/* Recent Threats and Agents */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Recent Threats */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Threats</h3>
              <Badge variant="danger">{threats.length} Active</Badge>
            </div>
          </div>
          <div className="p-6">
            <DataTable
              data={(threatsList || []).slice(0, 5)}
              columns={threatColumns}
              emptyMessage="No active threats detected"
            />
          </div>
        </div>

        {/* Agent Status */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Agent Fleet</h3>
              <div className="flex space-x-2">
                <Badge variant="success">{agentMetrics.online} Online</Badge>
                <Badge variant="danger">{agentMetrics.offline} Offline</Badge>
              </div>
            </div>
          </div>
          <div className="p-6">
            <DataTable
              data={(agentsList || []).slice(0, 5)}
              columns={agentColumns}
              emptyMessage="No agents registered"
            />
          </div>
        </div>
      </div>
    </div>
  );
}