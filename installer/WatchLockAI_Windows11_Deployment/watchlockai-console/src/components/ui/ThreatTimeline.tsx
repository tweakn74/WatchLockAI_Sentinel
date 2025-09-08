import React, { useState } from 'react';
import { Badge } from './badge';
import { Button } from './Button';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { 
  Clock, 
  AlertTriangle, 
  Shield, 
  Eye, 
  Play, 
  ChevronDown, 
  ChevronRight,
  Filter,
  Download
} from 'lucide-react';
import { cn, formatTimeAgo } from '../../lib/utils';

interface TimelineEvent {
  timestamp: string;
  event: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  details?: string;
  source?: string;
  evidence?: string[];
  mitre_technique?: string;
}

interface ThreatTimelineProps {
  threatId: string;
  title: string;
  events: TimelineEvent[];
  onEventClick?: (event: TimelineEvent) => void;
  onExportTimeline?: () => void;
  className?: string;
}

const severityConfig = {
  low: {
    color: 'bg-blue-500',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  },
  medium: {
    color: 'bg-yellow-500',
    textColor: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200'
  },
  high: {
    color: 'bg-orange-500',
    textColor: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200'
  },
  critical: {
    color: 'bg-red-500',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  }
};

export function ThreatTimeline({
  threatId,
  title,
  events,
  onEventClick,
  onExportTimeline,
  className
}: ThreatTimelineProps) {
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set());
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);
  
  const sortedEvents = [...(events || [])].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  
  const filteredEvents = filterSeverity 
    ? (sortedEvents || []).filter(event => event.severity === filterSeverity)
    : (sortedEvents || []);

  const toggleEventExpansion = (index: number) => {
    const newExpanded = new Set(expandedEvents);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedEvents(newExpanded);
  };

  const handleEventClick = (event: TimelineEvent) => {
    onEventClick?.(event);
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-gray-500" />
              <span>Threat Timeline</span>
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">{title}</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline" size="sm" onClick={onExportTimeline}>
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
        
        {/* Severity Filters */}
        <div className="flex space-x-2 mt-4">
          <button
            onClick={() => setFilterSeverity(null)}
            className={cn(
              'px-3 py-1 text-xs rounded-full border transition-colors',
              !filterSeverity 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
            )}
          >
            All ({events.length})
          </button>
          {Object.keys(severityConfig).map((severity) => {
            const count = (events || []).filter(e => e.severity === severity).length;
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
      
      <CardContent>
        <div className="space-y-4">
          {filteredEvents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-8 h-8 mx-auto mb-2" />
              <p>No timeline events found</p>
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
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
              
              {filteredEvents.map((event, index) => {
                const config = severityConfig[event.severity];
                const isExpanded = expandedEvents.has(index);
                
                return (
                  <div key={index} className="relative flex items-start space-x-4 pb-6">
                    {/* Timeline dot */}
                    <div className={cn(
                      'flex-shrink-0 w-3 h-3 rounded-full border-2 border-white z-10',
                      config.color
                    )} />
                    
                    {/* Event content */}
                    <div className="flex-1 min-w-0">
                      <div 
                        className={cn(
                          'bg-white border rounded-lg p-4 cursor-pointer hover:shadow-sm transition-all',
                          config.borderColor
                        )}
                        onClick={() => handleEventClick(event)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <Badge className={`${config.textColor} bg-white border-current`}>
                                {event.severity.toUpperCase()}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                {formatTimeAgo(event.timestamp)}
                              </span>
                              {event.mitre_technique && (
                                <Badge variant="outline" className="text-xs">
                                  {event.mitre_technique}
                                </Badge>
                              )}
                            </div>
                            
                            <h4 className="font-medium text-gray-900 mb-1">
                              {event.event}
                            </h4>
                            
                            {event.source && (
                              <p className="text-sm text-gray-600 mb-2">
                                Source: {event.source}
                              </p>
                            )}
                            
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-gray-500">
                                {new Date(event.timestamp).toLocaleString()}
                              </span>
                              
                              <div className="flex space-x-2">
                                {(event.details || event.evidence) && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleEventExpansion(index);
                                    }}
                                    className="text-xs"
                                  >
                                    {isExpanded ? (
                                      <ChevronDown className="w-4 h-4" />
                                    ) : (
                                      <ChevronRight className="w-4 h-4" />
                                    )}
                                    <span className="ml-1">
                                      {isExpanded ? 'Less' : 'More'}
                                    </span>
                                  </Button>
                                )}
                                
                                <Button variant="ghost" size="sm" className="text-xs">
                                  <Eye className="w-4 h-4 mr-1" />
                                  Investigate
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Expanded details */}
                        {isExpanded && (event.details || event.evidence) && (
                          <div className={cn('mt-4 pt-4 border-t', config.borderColor)}>
                            {event.details && (
                              <div className="mb-3">
                                <h5 className="text-sm font-medium text-gray-700 mb-1">Details</h5>
                                <p className="text-sm text-gray-600">{event.details}</p>
                              </div>
                            )}
                            
                            {event.evidence && event.evidence.length > 0 && (
                              <div>
                                <h5 className="text-sm font-medium text-gray-700 mb-2">Evidence</h5>
                                <div className="space-y-1">
                                  {event.evidence.map((item, evidenceIndex) => (
                                    <div 
                                      key={evidenceIndex} 
                                      className="text-sm text-gray-600 bg-gray-50 p-2 rounded font-mono"
                                    >
                                      {item}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}