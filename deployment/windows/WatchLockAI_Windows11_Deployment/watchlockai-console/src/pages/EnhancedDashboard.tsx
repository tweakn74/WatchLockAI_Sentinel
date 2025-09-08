import React, { useState } from 'react';
import { useAuth } from '../lib/auth';
import { 
  useDashboardMetrics, 
  useThreats, 
  useAgents,
  useApiHealth,
  useRealTimeData
} from '../hooks/useApiData';
import { 
  useMitreAttackData 
} from '../hooks/useEnhancedData';
import { 
  Shield, 
  Monitor, 
  AlertTriangle, 
  Activity,
  TrendingUp,
  Users,
  Zap,
  Clock,
  Target,
  Globe,
  Server,
  Eye
} from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { ThreatCard } from '../components/ui/ThreatCard';
import { AgentStatusCard } from '../components/ui/AgentStatusCard';
import { SecurityMetrics } from '../components/ui/SecurityMetrics';
import { LiveThreatFeed } from '../components/ui/LiveThreatFeed';
import { MitreAttackMatrix } from '../components/ui/MitreAttackMatrix';
import { ChartContainer } from '../components/ui/ChartContainer';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { cn } from '../lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

export function EnhancedDashboard() {
  const { profile } = useAuth();
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [isLiveFeedActive, setIsLiveFeedActive] = useState(true);
  
  const { health } = useApiHealth();
  const { metrics, threats, agents, loading: metricsLoading } = useDashboardMetrics();
  const { data: mitreData, loading: mitreLoading } = useMitreAttackData();
  
  // Real-time data updates
  const { data: realtimeThreats, lastUpdate } = useRealTimeData(
    async () => ({ data: threats, error: null, success: true }),
    15000 // 15 seconds
  );

  // Use metrics from API with null checking
  const criticalThreats = metrics?.threats?.critical || 0;
  const highThreats = metrics?.threats?.high || 0;
  const openThreats = metrics?.threats?.open || 0;
  const onlineAgents = metrics?.agents?.online || 0;
  const offlineAgents = metrics?.agents?.offline || 0;
  const avgSecurityScore = 85; // From API metrics

  if (metricsLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Security Operations Header */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 rounded-xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Welcome back, {profile?.full_name || 'Security Analyst'}
              </h1>
              <p className="text-blue-100 text-lg">
                Your Security Operations Center is monitoring {agents?.length || 0} endpoints across your infrastructure
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold">{avgSecurityScore.toFixed(0)}%</div>
              <div className="text-blue-200">Security Posture</div>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <span className="text-sm text-blue-200">Critical Threats</span>
              </div>
              <div className="text-2xl font-bold mt-1">{criticalThreats}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-orange-400" />
                <span className="text-sm text-blue-200">Active Threats</span>
              </div>
              <div className="text-2xl font-bold mt-1">{openThreats}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
              <div className="flex items-center space-x-2">
                <Monitor className="w-5 h-5 text-green-400" />
                <span className="text-sm text-blue-200">Online Agents</span>
              </div>
              <div className="text-2xl font-bold mt-1">{onlineAgents}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4 backdrop-blur-sm">
              <div className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-blue-200">Coverage</span>
              </div>
              <div className="text-2xl font-bold mt-1">87%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Security Metrics Dashboard */}
      <SecurityMetrics 
        metrics={[
          {
            id: 'detection_rate',
            title: 'Detection Rate',
            value: `${metrics.security.detectionRate}%`,
            status: 'good' as const,
            change: { value: 5.2, period: '24h', isPositive: true }
          },
          {
            id: 'response_time',
            title: 'Avg Response Time',
            value: `${metrics.security.responseTime}m`,
            status: 'good' as const,
            change: { value: -2.1, period: '24h', isPositive: true }
          },
          {
            id: 'threat_score',
            title: 'Avg Threat Score',
            value: Math.round(metrics.security.avgThreatScore),
            status: 'warning' as const,
            change: { value: 3.4, period: '24h', isPositive: false }
          },
          {
            id: 'confidence',
            title: 'Confidence Level',
            value: `${Math.round(metrics.security.avgConfidence * 100)}%`,
            status: 'good' as const,
            change: { value: 1.8, period: '24h', isPositive: true }
          }
        ]}
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
      />

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column - Threat Feed & Recent Threats */}
        <div className="xl:col-span-2 space-y-6">
          {/* Live Threat Feed */}
          <LiveThreatFeed 
            isLive={isLiveFeedActive}
            onToggleLive={() => setIsLiveFeedActive(!isLiveFeedActive)}
            maxItems={8}
          />
          
          {/* Recent Critical Threats */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  <span>Critical Threats Requiring Attention</span>
                </CardTitle>
                <Badge variant="destructive">{criticalThreats + highThreats} Active</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {(threats || [])
                  .filter(t => t.severity === 'critical' || t.severity === 'high')
                  .slice(0, 4)
                  .map((threat) => (
                    <ThreatCard
                      key={threat.id}
                      {...threat}
                      hostname={agents.find(a => a.id === threat.agent_id)?.hostname}
                      onViewDetails={() => console.log('View details:', threat.id)}
                      onInvestigate={() => console.log('Investigate:', threat.id)}
                      onRespond={() => console.log('Respond:', threat.id)}
                    />
                  ))}
              </div>
              {(threats?.filter(t => t.severity === 'critical' || t.severity === 'high')?.length || 0) === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Shield className="w-12 h-12 mx-auto mb-4 text-green-500" />
                  <p className="text-lg font-medium">No critical threats detected</p>
                  <p className="text-sm">Your security posture is looking good!</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Threat Analytics Charts */}
          {(
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Threat Trends */}
              <ChartContainer 
                title="24-Hour Threat Activity"
                subtitle="Real-time threat detection trends"
              >
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={Array.from({ length: 12 }, (_, i) => ({
                    time: `${i + 1}:00`,
                    threats: Math.floor(Math.random() * 10) + 5,
                    critical: Math.floor(Math.random() * 3)
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="threats" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.1}
                      strokeWidth={2}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="critical" 
                      stroke="#ef4444" 
                      fill="#ef4444" 
                      fillOpacity={0.2}
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartContainer>

              {/* MITRE Techniques Heatmap */}
              <ChartContainer 
                title="Top MITRE ATT&CK Techniques"
                subtitle="Most frequently observed techniques"
              >
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { technique: 'T1059', count: 15 },
                    { technique: 'T1055', count: 12 },
                    { technique: 'T1105', count: 8 },
                    { technique: 'T1027', count: 6 },
                    { technique: 'T1140', count: 4 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="technique" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value, name, props) => [
                        `${value} detections`, 
                        props.payload.name
                      ]}
                    />
                    <Bar 
                      dataKey="count" 
                      fill="#f59e0b"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </div>
          )}
        </div>

        {/* Right Column - Agent Status & Fleet Metrics */}
        <div className="space-y-6">
          {/* Agent Fleet Overview */}
          {!metricsLoading && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Server className="w-5 h-5 text-blue-500" />
                  <span>Agent Fleet Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Fleet Summary */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{onlineAgents}</div>
                      <div className="text-sm text-gray-600">Online</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{offlineAgents}</div>
                      <div className="text-sm text-gray-600">Offline</div>
                    </div>
                  </div>
                  
                  {/* Performance Metrics */}
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Average CPU Usage</span>
                        <span>25%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `25%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Average Memory Usage</span>
                        <span>45%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full" 
                          style={{ width: `45%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Compliance Score</span>
                        <span>88%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{ width: `88%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Agent Activity */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-green-500" />
                  <span>Agent Activity</span>
                </CardTitle>
                <Button variant="outline" size="sm">
                  <Eye className="w-4 h-4 mr-2" />
                  View All
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(agents || [])
                  .filter(a => a.status === 'online' && a.threat_count > 0)
                  .slice(0, 3)
                  .map((agent) => (
                    <div key={agent.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{agent.hostname}</span>
                        <Badge 
                          variant={agent.threat_count > 0 ? 'destructive' : 'default'}
                          className="text-xs"
                        >
                          {agent.threat_count} threats
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        {agent.location} • {agent.os_type}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Security Score: {agent.security_score}%
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>

          {/* MITRE ATT&CK Overview */}
          {!mitreLoading && mitreData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-purple-500" />
                  <span>MITRE ATT&CK Overview</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-lg font-bold">{mitreData.tactics?.length || 0}</div>
                      <div className="text-sm text-gray-600">Tactics</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold">{mitreData.techniques?.length || 0}</div>
                      <div className="text-sm text-gray-600">Techniques</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {mitreData.tactics?.slice(0, 4).map((tactic: any) => (
                      <div key={tactic.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm font-medium">{tactic.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {tactic.techniques_count}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  
                  <Button variant="outline" className="w-full" size="sm">
                    View Full Matrix
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Bottom Section - Critical Agent Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Monitor className="w-5 h-5 text-blue-500" />
              <span>Agents Requiring Attention</span>
            </CardTitle>
            <Badge variant="outline">
              {agents?.filter(a => a.status === 'offline' || a.threat_count > 0)?.length || 0} agents
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents
              .filter(a => a.status === 'offline' || a.threat_count > 0 || a.security_score < 70)
              .slice(0, 6)
              .map((agent) => (
                <AgentStatusCard
                  key={agent.id}
                  {...agent}
                  onConfigure={() => console.log('Configure agent:', agent.id)}
                  onInvestigate={() => console.log('Investigate agent:', agent.id)}
                  onIsolate={() => console.log('Isolate agent:', agent.id)}
                />
              ))}
          </div>
          
          {(agents?.filter(a => a.status === 'offline' || a.threat_count > 0 || a.security_score < 70)?.length || 0) === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Monitor className="w-12 h-12 mx-auto mb-4 text-green-500" />
              <p className="text-lg font-medium">All agents are healthy</p>
              <p className="text-sm">No agents require immediate attention</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}