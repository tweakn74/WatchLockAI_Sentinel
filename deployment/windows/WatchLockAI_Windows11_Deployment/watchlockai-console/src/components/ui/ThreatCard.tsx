import React from 'react';
import { Badge } from './badge';
import { Button } from './Button';
import { 
  AlertTriangle, 
  Shield, 
  Clock, 
  MapPin, 
  Monitor, 
  Eye,
  Play,
  MoreVertical
} from 'lucide-react';
import { cn, formatTimeAgo } from '../../lib/utils';

interface MitreTechnique {
  id: string;
  name: string;
  tactic: string;
}

interface ThreatCardProps {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  threat_type: string;
  threat_score: number;
  confidence_score: number;
  first_seen: string;
  last_seen: string;
  agent_id: string;
  hostname?: string;
  mitre_techniques: MitreTechnique[];
  kill_chain_phase: string;
  indicators?: {
    iocs: string[];
  };
  onViewDetails?: () => void;
  onInvestigate?: () => void;
  onRespond?: () => void;
}

const severityConfig = {
  critical: {
    color: 'bg-red-500',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: AlertTriangle
  },
  high: {
    color: 'bg-orange-500',
    textColor: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    icon: AlertTriangle
  },
  medium: {
    color: 'bg-yellow-500',
    textColor: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    icon: Shield
  },
  low: {
    color: 'bg-blue-500',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: Shield
  }
};

const statusConfig = {
  open: { color: 'bg-red-100 text-red-800', label: 'Open' },
  investigating: { color: 'bg-yellow-100 text-yellow-800', label: 'Investigating' },
  resolved: { color: 'bg-green-100 text-green-800', label: 'Resolved' },
  closed: { color: 'bg-gray-100 text-gray-800', label: 'Closed' }
};

export function ThreatCard({
  id,
  title,
  description,
  severity,
  status,
  threat_type,
  threat_score,
  confidence_score,
  first_seen,
  last_seen,
  agent_id,
  hostname,
  mitre_techniques,
  kill_chain_phase,
  indicators,
  onViewDetails,
  onInvestigate,
  onRespond
}: ThreatCardProps) {
  const config = severityConfig[severity];
  const SeverityIcon = config.icon;
  const statusStyle = statusConfig[status];

  return (
    <div className={cn(
      'bg-white rounded-lg border-2 shadow-sm hover:shadow-md transition-all duration-200',
      config.borderColor
    )}>
      {/* Header */}
      <div className={cn('p-4 rounded-t-lg', config.bgColor)}>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={cn('p-2 rounded-lg', config.color)}>
              <SeverityIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">{title}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <Badge className={statusStyle.color}>
                  {statusStyle.label}
                </Badge>
                <span className="text-sm text-gray-600">{threat_type}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-right">
              <div className="text-lg font-bold text-gray-900">{threat_score}</div>
              <div className="text-xs text-gray-500">Threat Score</div>
            </div>
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <p className="text-gray-700 text-sm mb-4 line-clamp-2">{description}</p>
        
        {/* Metrics Row */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">{Math.round(confidence_score * 100)}%</div>
            <div className="text-xs text-gray-500">Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">{mitre_techniques.length}</div>
            <div className="text-xs text-gray-500">MITRE TTPs</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">{indicators?.iocs.length || 0}</div>
            <div className="text-xs text-gray-500">IoCs</div>
          </div>
        </div>

        {/* MITRE Techniques */}
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-700 mb-2">MITRE ATT&CK Techniques</div>
          <div className="flex flex-wrap gap-1">
            {mitre_techniques.slice(0, 3).map((technique) => (
              <Badge 
                key={technique.id} 
                variant="outline" 
                className="text-xs"
                title={technique.name}
              >
                {technique.id}
              </Badge>
            ))}
            {mitre_techniques.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{mitre_techniques.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Kill Chain Phase */}
        <div className="mb-4">
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">Kill Chain: {kill_chain_phase}</span>
          </div>
        </div>

        {/* Agent Info */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Monitor className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">{hostname || agent_id}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">{formatTimeAgo(first_seen)}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onViewDetails}
            className="flex items-center space-x-1"
          >
            <Eye className="w-4 h-4" />
            <span>Details</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onInvestigate}
            className="flex items-center space-x-1"
          >
            <Shield className="w-4 h-4" />
            <span>Investigate</span>
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={onRespond}
            className="flex items-center space-x-1"
          >
            <Play className="w-4 h-4" />
            <span>Respond</span>
          </Button>
        </div>
      </div>
    </div>
  );
}