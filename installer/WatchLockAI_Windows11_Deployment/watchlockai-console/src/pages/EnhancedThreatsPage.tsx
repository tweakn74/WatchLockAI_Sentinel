import React, { useState } from 'react';
import { useThreats, useUpdateThreatStatus } from '../hooks/useApiData';
import { useMitreAttackData } from '../hooks/useEnhancedData';
import { 
  Shield, 
  AlertTriangle, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Play, 
  MoreVertical,
  Target,
  Clock,
  TrendingUp,
  Activity
} from 'lucide-react';
import { ThreatCard } from '../components/ui/ThreatCard';
import { ThreatTimeline } from '../components/ui/ThreatTimeline';
import { MitreAttackMatrix } from '../components/ui/MitreAttackMatrix';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/Button';
import { FilterTabs } from '../components/ui/FilterTabs';
import { cn } from '../lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export function EnhancedThreatsPage() {
  const { data: threats, loading } = useThreats();
  const { data: mitreData, loading: mitreLoading } = useMitreAttackData();
  const { updateStatus } = useUpdateThreatStatus();
  
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'cards' | 'table' | 'timeline'>('cards');
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showMitreMatrix, setShowMitreMatrix] = useState(false);

  // Filter threats based on selected filters (with null safety)
  const threatList = threats || [];
  const filteredThreats = threatList.filter(threat => {
    const matchesSearch = threat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         threat.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = !filterSeverity || threat.severity === filterSeverity;
    const matchesStatus = !filterStatus || threat.status === filterStatus;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  // Calculate metrics (with null safety)
  const criticalThreats = (threatList || []).filter(t => t.severity === 'critical').length;
  const highThreats = (threatList || []).filter(t => t.severity === 'high').length;
  const openThreats = (threatList || []).filter(t => t.status === 'open').length;
  const avgThreatScore = threatList.reduce((sum, t) => sum + t.threat_score, 0) / Math.max(threatList.length, 1);
  const avgConfidenceScore = threatList.reduce((sum, t) => sum + t.confidence_score, 0) / Math.max(threatList.length, 1);

  // Generate threat trends data
  const threatTrends = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date();
    hour.setHours(hour.getHours() - (23 - i));
    return {
      time: hour.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      threats: Math.floor(Math.random() * 8) + 2,
      critical: Math.floor(Math.random() * 3)
    };
  });

  // Generate MITRE technique frequency
  const mitreFrequency = threatList.reduce((acc: any, threat) => {
    threat.mitre_techniques.forEach(technique => {
      acc[technique.id] = (acc[technique.id] || 0) + 1;
    });
    return acc;
  }, {});

  const topMitreTechniques = Object.entries(mitreFrequency)
    .sort(([,a], [,b]) => (b as number) - (a as number))
    .slice(0, 8)
    .map(([id, count]) => ({ id, count, name: id }));

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
      <div className="bg-gradient-to-r from-red-600 via-orange-600 to-red-700 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Threat Detection & Analysis</h1>
            <p className="text-red-100">
              Real-time threat monitoring and incident response management
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{threatList.length}</div>
            <div className="text-red-200">Total Threats</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-red-200">Critical</div>
            <div className="text-xl font-bold">{criticalThreats}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-red-200">High</div>
            <div className="text-xl font-bold">{highThreats}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-red-200">Open</div>
            <div className="text-xl font-bold">{openThreats}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-red-200">Avg Score</div>
            <div className="text-xl font-bold">{avgThreatScore.toFixed(0)}</div>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
            <div className="text-sm text-red-200">Confidence</div>
            <div className="text-xl font-bold">{(avgConfidenceScore * 100).toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span>24-Hour Threat Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={threatTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="threats" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Total Threats"
                />
                <Line 
                  type="monotone" 
                  dataKey="critical" 
                  stroke="#ef4444" 
                  strokeWidth={2}
                  name="Critical Threats"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top MITRE Techniques */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-purple-500" />
              <span>Top MITRE ATT&CK Techniques</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topMitreTechniques}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="id" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
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
              placeholder="Search threats..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
            />
          </div>
          
          {/* Severity Filter */}
          <div className="flex space-x-1">
            <button
              onClick={() => setFilterSeverity(null)}
              className={cn(
                'px-3 py-2 text-sm rounded-lg transition-colors',
                !filterSeverity ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              All
            </button>
            {['critical', 'high', 'medium', 'low'].map((severity) => (
              <button
                key={severity}
                onClick={() => setFilterSeverity(severity)}
                className={cn(
                  'px-3 py-2 text-sm rounded-lg transition-colors capitalize',
                  filterSeverity === severity ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                {severity}
              </button>
            ))}
          </div>

          {/* Status Filter */}
          <div className="flex space-x-1">
            {['open', 'investigating', 'resolved'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(filterStatus === status ? null : status)}
                className={cn(
                  'px-3 py-2 text-sm rounded-lg transition-colors capitalize',
                  filterStatus === status ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {[
              { mode: 'cards', icon: Shield, label: 'Cards' },
              { mode: 'timeline', icon: Clock, label: 'Timeline' }
            ].map(({ mode, icon: Icon, label }) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode as any)}
                className={cn(
                  'flex items-center space-x-2 px-3 py-1 text-sm rounded-md transition-colors',
                  viewMode === mode
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </button>
            ))}
          </div>

          <Button 
            variant="outline" 
            onClick={() => setShowMitreMatrix(!showMitreMatrix)}
            className="flex items-center space-x-2"
          >
            <Target className="w-4 h-4" />
            <span>MITRE Matrix</span>
          </Button>

          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filters
          </Button>

          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* MITRE ATT&CK Matrix */}
      {showMitreMatrix && !mitreLoading && mitreData && (
        <MitreAttackMatrix
          tactics={mitreData.tactics}
          techniques={mitreData.techniques}
          threatMappings={Object.entries(mitreFrequency).map(([technique_id, count]) => ({
            technique_id,
            threat_count: count as number,
            last_seen: new Date().toISOString()
          }))}
          showHeatmap={true}
        />
      )}

      {/* Threat Content */}
      {viewMode === 'cards' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredThreats.map((threat) => (
            <ThreatCard
              key={threat.id}
              {...threat}
              onViewDetails={() => setSelectedThreat(threat)}
              onInvestigate={() => {
                // Start investigation workflow
                updateStatus(threat.id, 'investigating');
              }}
              onRespond={() => {
                // Quick response action
                updateStatus(threat.id, 'resolved');
              }}
            />
          ))}
        </div>
      )}

      {viewMode === 'timeline' && (
        <div className="space-y-6">
          {filteredThreats.slice(0, 5).map((threat) => (
            <ThreatTimeline
              key={threat.id}
              threatId={threat.id}
              title={threat.title}
              events={threat.timeline}
              onEventClick={(event) => {
                // Handle timeline event interaction
                console.log('Timeline event selected:', event);
              }}
              onExportTimeline={() => {
                // Export timeline functionality
                console.log('Exporting timeline for threat:', threat.id);
              }}
            />
          ))}
        </div>
      )}

      {filteredThreats.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Shield className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No threats found</h3>
            <p className="text-gray-600">
              {searchTerm || filterSeverity || filterStatus
                ? 'Try adjusting your search criteria or filters'
                : 'Your environment is secure - no active threats detected'}
            </p>
            {(searchTerm || filterSeverity || filterStatus) && (
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => {
                  setSearchTerm('');
                  setFilterSeverity(null);
                  setFilterStatus(null);
                }}
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Threat Details Modal */}
      {selectedThreat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedThreat.title}</h2>
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge className={`${
                      selectedThreat.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      selectedThreat.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      selectedThreat.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {selectedThreat.severity.toUpperCase()}
                    </Badge>
                    <Badge variant="outline">
                      {selectedThreat.threat_type}
                    </Badge>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedThreat(null)}
                  className="text-2xl"
                >
                  x
                </Button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Description</h3>
                    <p className="text-gray-700">{selectedThreat.description}</p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">MITRE ATT&CK Techniques</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedThreat.mitre_techniques.map((technique: any) => (
                        <Badge key={technique.id} variant="outline">
                          {technique.id} - {technique.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Indicators of Compromise</h3>
                    <div className="space-y-2">
                      {selectedThreat.indicators?.iocs.map((ioc: string, index: number) => (
                        <div key={index} className="bg-gray-50 p-2 rounded font-mono text-sm">
                          {ioc}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Threat Intelligence</h3>
                    <div className="space-y-2 text-sm">
                      <div>Threat Score: <span className="font-medium">{selectedThreat.threat_score}/100</span></div>
                      <div>Confidence: <span className="font-medium">{(selectedThreat.confidence_score * 100).toFixed(0)}%</span></div>
                      <div>Kill Chain Phase: <span className="font-medium">{selectedThreat.kill_chain_phase}</span></div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Affected Assets</h3>
                    <div className="space-y-1">
                      {selectedThreat.affected_assets.map((asset: string, index: number) => (
                        <div key={index} className="bg-blue-50 p-2 rounded text-sm">
                          {asset}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Response Actions</h3>
                    <div className="space-y-2">
                      {selectedThreat.response_actions.map((action: string, index: number) => (
                        <Button key={index} variant="outline" size="sm" className="mr-2 mb-2">
                          {action.replace('_', ' ').toUpperCase()}
                        </Button>
                      ))}
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