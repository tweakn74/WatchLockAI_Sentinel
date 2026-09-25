import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Badge } from './badge';
import { Button } from './Button';
import { 
  Radio, 
  Pause, 
  Play, 
  AlertTriangle, 
  Shield, 
  Clock, 
  Activity,
  Filter,
  Settings,
  Maximize2
} from 'lucide-react';
import { cn, formatTimeAgo } from '../../lib/utils';

interface LiveThreat {
  id: string;
  timestamp: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  agent_hostname: string;
  threat_type: string;
  status: 'new' | 'acknowledged' | 'investigating';
  mitre_technique?: string;
}

interface LiveThreatFeedProps {
  threats?: LiveThreat[];
  isLive?: boolean;
  onToggleLive?: () => void;
  onThreatClick?: (threat: LiveThreat) => void;
  onAcknowledge?: (threatId: string) => void;
  onInvestigate?: (threatId: string) => void;
  maxItems?: number;
  className?: string;
}

const severityConfig = {
  critical: {
    color: 'bg-red-500',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    pulseColor: 'animate-pulse text-red-500'
  },
  high: {
    color: 'bg-orange-500',
    textColor: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    pulseColor: 'animate-pulse text-orange-500'
  },
  medium: {
    color: 'bg-yellow-500',
    textColor: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    pulseColor: 'animate-pulse text-yellow-500'
  },
  low: {
    color: 'bg-blue-500',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    pulseColor: 'animate-pulse text-blue-500'
  }
};

const statusConfig = {
  new: { label: 'New', color: 'bg-red-100 text-red-800' },
  acknowledged: { label: 'Acknowledged', color: 'bg-yellow-100 text-yellow-800' },
  investigating: { label: 'Investigating', color: 'bg-blue-100 text-blue-800' }
};

// Sample live threats data
const sampleThreats: LiveThreat[] = [
  {
    id: 'live_001',
    timestamp: new Date().toISOString(),
    title: 'Suspicious PowerShell Execution Detected',
    severity: 'critical',
    agent_hostname: 'DESKTOP-ABC123',
    threat_type: 'Malware',
    status: 'new',
    mitre_technique: 'T1059.001'
  },
  {
    id: 'live_002',
    timestamp: new Date(Date.now() - 30000).toISOString(),
    title: 'Unusual Network Traffic Pattern',
    severity: 'high',
    agent_hostname: 'SRV-FILE01',
    threat_type: 'Command and Control',
    status: 'acknowledged',
    mitre_technique: 'T1071.001'
  },
  {
    id: 'live_003',
    timestamp: new Date(Date.now() - 120000).toISOString(),
    title: 'Failed Login Attempts',
    severity: 'medium',
    agent_hostname: 'LAPTOP-DEF456',
    threat_type: 'Credential Access',
    status: 'investigating',
    mitre_technique: 'T1110'
  }
];

export function LiveThreatFeed({
  threats = sampleThreats,
  isLive = true,
  onToggleLive,
  onThreatClick,
  onAcknowledge,
  onInvestigate,
  maxItems = 10,
  className
}: LiveThreatFeedProps) {
  const [displayThreats, setDisplayThreats] = useState<LiveThreat[]>((threats || []).slice(0, maxItems));
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Simulate live updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      // Simulate new threat
      const newThreat: LiveThreat = {
        id: `live_${Date.now()}`,
        timestamp: new Date().toISOString(),
        title: `New threat detected - ${Math.random().toString(36).substr(2, 9)}`,
        severity: ['critical', 'high', 'medium', 'low'][Math.floor(Math.random() * 4)] as any,
        agent_hostname: `HOST-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
        threat_type: ['Malware', 'Phishing', 'Command and Control', 'Data Exfiltration'][Math.floor(Math.random() * 4)],
        status: 'new',
        mitre_technique: `T${Math.floor(Math.random() * 9999)}`
      };

      setDisplayThreats(prev => [newThreat, ...prev].slice(0, maxItems));
      setLastUpdate(new Date());
    }, 15000); // New threat every 15 seconds

    return () => clearInterval(interval);
  }, [isLive, maxItems]);

  const filteredThreats = filterSeverity
    ? (displayThreats || []).filter(threat => threat.severity === filterSeverity)
    : (displayThreats || []);

  const handleThreatClick = (threat: LiveThreat) => {
    onThreatClick?.(threat);
  };

  const handleAcknowledge = (threatId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    onAcknowledge?.(threatId);
    
    // Update local state
    setDisplayThreats(prev => 
      prev.map(threat => 
        threat.id === threatId 
          ? { ...threat, status: 'acknowledged' }
          : threat
      )
    );
  };

  const handleInvestigate = (threatId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    onInvestigate?.(threatId);
    
    // Update local state
    setDisplayThreats(prev => 
      prev.map(threat => 
        threat.id === threatId 
          ? { ...threat, status: 'investigating' }
          : threat
      )
    );
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <span>Live Threat Feed</span>
            </CardTitle>
            
            {isLive && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm text-green-600 font-medium">LIVE</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onToggleLive}
              className="flex items-center space-x-2"
            >
              {isLive ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Pause</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Resume</span>
                </>
              )}
            </Button>
            
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
            
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>
        
        {/* Status Info */}
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredThreats.length} of {displayThreats.length} threats</span>
          <span>Last update: {formatTimeAgo(lastUpdate.toISOString())}</span>
        </div>
        
        {/* Severity Filters */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilterSeverity(null)}
            className={cn(
              'px-3 py-1 text-xs rounded-full border transition-colors',
              !filterSeverity 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
            )}
          >
            All ({displayThreats.length})
          </button>
          {Object.keys(severityConfig).map((severity) => {
            const count = (displayThreats || []).filter(t => t.severity === severity).length;
            const config = severityConfig[severity as keyof typeof severityConfig];
            
            return (
              <button
                key={severity}
                onClick={() => setFilterSeverity(severity)}
                className={cn(
                  'px-3 py-1 text-xs rounded-full border transition-colors capitalize',
                  filterSeverity === severity
                    ? `${config.color} text-white border-current`
                    : `${config.textColor} bg-white border-current hover:${config.bgColor}`
                )}
              >
                {severity} ({count})
              </button>
            );
          })}
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="max-h-96 overflow-y-auto">
          {filteredThreats.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Radio className="w-8 h-8 mx-auto mb-2" />
              <p>No live threats detected</p>
              {filterSeverity && (
                <button 
                  onClick={() => setFilterSeverity(null)}
                  className="text-blue-600 hover:underline text-sm mt-2"
                >
                  Clear filters
                </button>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredThreats.map((threat) => {
                const config = severityConfig[threat.severity];
                const statusStyle = statusConfig[threat.status];
                
                return (
                  <div 
                    key={threat.id}
                    className={cn(
                      'p-4 hover:bg-gray-50 cursor-pointer transition-colors',
                      threat.status === 'new' ? 'bg-blue-50' : ''
                    )}
                    onClick={() => handleThreatClick(threat)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        {/* Severity indicator */}
                        <div className={cn(
                          'w-3 h-3 rounded-full mt-1 flex-shrink-0',
                          config.color,
                          threat.status === 'new' ? config.pulseColor : ''
                        )} />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h4 className="font-medium text-gray-900 truncate">
                              {threat.title}
                            </h4>
                            <Badge className={statusStyle.color}>
                              {statusStyle.label}
                            </Badge>
                          </div>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                            <span>Host: {threat.agent_hostname}</span>
                            <span>Type: {threat.threat_type}</span>
                            {threat.mitre_technique && (
                              <Badge variant="outline" className="text-xs">
                                {threat.mitre_technique}
                              </Badge>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-2 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            <span>{formatTimeAgo(threat.timestamp)}</span>
                            <span>*</span>
                            <span className={config.textColor}>
                              {threat.severity.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Actions */}
                      <div className="flex space-x-2 ml-4">
                        {threat.status === 'new' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => handleAcknowledge(threat.id, e)}
                            className="text-xs"
                          >
                            Acknowledge
                          </Button>
                        )}
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => handleInvestigate(threat.id, e)}
                          className="text-xs flex items-center space-x-1"
                        >
                          <Shield className="w-3 h-3" />
                          <span>Investigate</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {/* Feed Controls */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Radio className={cn('w-4 h-4', isLive ? 'text-green-600' : 'text-gray-400')} />
              <span>{isLive ? 'Live monitoring active' : 'Live monitoring paused'}</span>
            </div>
            
            <Button variant="outline" size="sm">
              <Maximize2 className="w-4 h-4 mr-2" />
              View All Threats
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}