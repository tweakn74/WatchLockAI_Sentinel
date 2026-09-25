import React, { useState } from 'react';
import { useAgents, useUpdateAgentStatus } from '../hooks/useApiData';
import { 
  Monitor, 
  Server, 
  Smartphone, 
  Search, 
  Filter, 
  Download, 
  Settings, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Wifi,
  WifiOff,
  MapPin,
  Cpu,
  HardDrive,
  Shield
} from 'lucide-react';
import { AgentStatusCard } from '../components/ui/AgentStatusCard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts';

export function EnhancedAgentsPage() {
  const { data: agents, loading } = useAgents();
  const { updateStatus } = useUpdateAgentStatus();
  
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [filterLocation, setFilterLocation] = useState<string | null>(null);
  const [filterOs, setFilterOs] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter agents based on selected filters (with null safety)
  const agentList = agents || [];
  const filteredAgents = (agentList || []).filter(agent => {
    const matchesSearch = agent.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.ip_address.includes(searchTerm) ||
                         agent.user.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !filterStatus || agent.status === filterStatus;
    const matchesLocation = !filterLocation || agent.location.toLowerCase().includes(filterLocation.toLowerCase());
    const matchesOs = !filterOs || agent.os_type.toLowerCase().includes(filterOs.toLowerCase());
    return matchesSearch && matchesStatus && matchesLocation && matchesOs;
  });

  // Calculate metrics (with null safety)
  const onlineAgents = (agentList || []).filter(a => a.status === 'online').length;
  const offlineAgents = (agentList || []).filter(a => a.status === 'offline').length;
  const errorAgents = (agentList || []).filter(a => a.status === 'error').length;
  const avgSecurityScore = agentList.reduce((sum, a) => sum + (a.security_score || 0), 0) / Math.max(agentList.length, 1);
  const avgPerformanceScore = agentList.reduce((sum, a) => sum + (a.performance_score || 0), 0) / Math.max(agentList.length, 1);
  const complianceRate = (agentList || []).filter(a => 
    a.policy_compliance && Object.values(a.policy_compliance).every(Boolean)
  ).length / Math.max((agentList || []).length, 1) * 100;

  // Generate analytics data
  const osDistribution = agentList.reduce((acc: any, agent) => {
    acc[agent.os_type] = (acc[agent.os_type] || 0) + 1;
    return acc;
  }, {});

  const osData = Object.entries(osDistribution).map(([os, count]) => ({
    name: os,
    value: count,
    fill: os.includes('Windows') ? '#0078d4' : os.includes('Linux') ? '#f68e56' : os.includes('macOS') ? '#000000' : '#6b7280'
  }));

  const locationDistribution = agentList.reduce((acc: any, agent) => {
    const location = agent.location.split(' - ')[0] || agent.location;
    acc[location] = (acc[location] || 0) + 1;
    return acc;
  }, {});

  const locationData = Object.entries(locationDistribution).map(([location, count]) => ({
    location,
    count
  }));

  // Performance trends (sample data)
  const performanceTrends = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date();
    hour.setHours(hour.getHours() - (23 - i));
    return {
      time: hour.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      avgCpu: Math.random() * 40 + 10,
      avgMemory: Math.random() * 30 + 40,
      avgDisk: Math.random() * 20 + 50
    };
  });

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-700 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Agent Fleet Management</h1>
            <p className="text-blue-100">
              Monitor and manage your deployed security agents across all endpoints
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{agentList.length}</div>
            <div className="text-blue-200">Total Agents</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="flex items-center space-x-2">
              <Wifi className="w-4 h-4 text-green-300" />
              <span className="text-sm text-blue-200">Online</span>
            </div>
            <div className="text-xl font-bold">{onlineAgents}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="flex items-center space-x-2">
              <WifiOff className="w-4 h-4 text-red-300" />
              <span className="text-sm text-blue-200">Offline</span>
            </div>
            <div className="text-xl font-bold">{offlineAgents}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-blue-200">Security Score</div>
            <div className="text-xl font-bold">{avgSecurityScore.toFixed(0)}%</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-blue-200">Performance</div>
            <div className="text-xl font-bold">{avgPerformanceScore.toFixed(0)}%</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-blue-200">Compliance</div>
            <div className="text-xl font-bold">{complianceRate.toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* OS Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Monitor className="w-5 h-5 text-blue-500" />
              <span>Operating System Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={osData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {osData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {osData.map((entry) => (
                <div key={entry.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: entry.fill }}
                    />
                    <span>{entry.name}</span>
                  </div>
                  <span className="font-medium">{String(entry.value)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Location Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-green-500" />
              <span>Location Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={locationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="location" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span>24-Hour Performance</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={performanceTrends.slice(-12)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="avgCpu" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  name="CPU %"
                />
                <Line 
                  type="monotone" 
                  dataKey="avgMemory" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  name="Memory %"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
            />
          </div>
          
          {/* Status Filter */}
          <div className="flex space-x-1">
            <button
              onClick={() => setFilterStatus(null)}
              className={cn(
                'px-3 py-2 text-sm rounded-lg transition-colors',
                !filterStatus ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              All Status
            </button>
            {['online', 'offline', 'error'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={cn(
                  'px-3 py-2 text-sm rounded-lg transition-colors capitalize',
                  filterStatus === status ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                {status}
              </button>
            ))}
          </div>

          {/* OS Filter */}
          <div className="flex space-x-1">
            {['Windows', 'Linux', 'macOS'].map((os) => (
              <button
                key={os}
                onClick={() => setFilterOs(filterOs === os ? null : os)}
                className={cn(
                  'px-3 py-2 text-sm rounded-lg transition-colors',
                  filterOs === os ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                {os}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filters
          </Button>
          
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Bulk Actions
          </Button>

          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => (
          <AgentStatusCard
            key={agent.id}
            {...agent}
            onConfigure={() => setSelectedAgent(agent)}
            onInvestigate={() => {
              // Start agent investigation
              console.log('Starting investigation for agent:', agent.id);
            }}
            onIsolate={() => {
              // Isolate agent from network
              updateStatus(agent.id, 'offline');
            }}
          />
        ))}
      </div>

      {filteredAgents.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Monitor className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No agents found</h3>
            <p className="text-gray-600">
              {searchTerm || filterStatus || filterOs
                ? 'Try adjusting your search criteria or filters'
                : 'No agents are currently deployed'}
            </p>
            {(searchTerm || filterStatus || filterOs) && (
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => {
                  setSearchTerm('');
                  setFilterStatus(null);
                  setFilterOs(null);
                }}
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedAgent.hostname}</h2>
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge className={cn(
                      selectedAgent.status === 'online' ? 'bg-green-100 text-green-800' :
                      selectedAgent.status === 'offline' ? 'bg-gray-100 text-gray-800' :
                      'bg-red-100 text-red-800'
                    )}>
                      {selectedAgent.status.toUpperCase()}
                    </Badge>
                    <Badge variant="outline">
                      {selectedAgent.os_type}
                    </Badge>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedAgent(null)}
                  className="text-2xl"
                >
                  x
                </Button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">System Information</h3>
                    <div className="space-y-2 text-sm">
                      <div>IP Address: <span className="font-medium">{selectedAgent.ip_address}</span></div>
                      <div>OS Version: <span className="font-medium">{selectedAgent.os_version}</span></div>
                      <div>Agent Version: <span className="font-medium">{selectedAgent.agent_version}</span></div>
                      <div>Location: <span className="font-medium">{selectedAgent.location}</span></div>
                      <div>User: <span className="font-medium">{selectedAgent.user}</span></div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Performance Metrics</h3>
                    <div className="space-y-3">
                      {selectedAgent.status === 'online' && (
                        <>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">CPU Usage</span>
                            <span className="font-medium">{selectedAgent.cpu_usage}%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Memory Usage</span>
                            <span className="font-medium">{selectedAgent.memory_usage}%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Disk Usage</span>
                            <span className="font-medium">{selectedAgent.disk_usage}%</span>
                          </div>
                        </>
                      )}
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Performance Score</span>
                        <span className="font-medium">{selectedAgent.performance_score}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Security Score</span>
                        <span className="font-medium">{selectedAgent.security_score}%</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Security Configuration</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedAgent.configuration).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-sm capitalize">{key.replace('_', ' ')}</span>
                          {value ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Policy Compliance</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedAgent.policy_compliance).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-sm capitalize">{key}</span>
                          {value ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-500" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Threat Activity</h3>
                    <div className="space-y-2 text-sm">
                      <div>Threats Detected: <span className="font-medium">{selectedAgent.threat_count}</span></div>
                      <div>Events Today: <span className="font-medium">{selectedAgent.events_today}</span></div>
                      <div>Processes Monitored: <span className="font-medium">{selectedAgent.processes_monitored}</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}