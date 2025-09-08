import React from 'react';
import { Badge } from './badge';
import { Button } from './Button';
import { 
  Monitor, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  Settings,
  MoreVertical,
  Wifi,
  WifiOff
} from 'lucide-react';
import { cn, formatTimeAgo } from '../../lib/utils';

interface PolicyCompliance {
  antimalware: boolean;
  firewall: boolean;
  encryption: boolean;
  patching: boolean;
}

interface AgentStatusCardProps {
  id: string;
  hostname: string;
  ip_address: string;
  os_type: string;
  os_version: string;
  status: 'online' | 'offline' | 'error';
  agent_version: string;
  last_heartbeat: string;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  location: string;
  user: string;
  tags: string[];
  policy_compliance: PolicyCompliance;
  threat_count: number;
  last_threat?: string;
  performance_score: number;
  security_score: number;
  onConfigure?: () => void;
  onInvestigate?: () => void;
  onIsolate?: () => void;
}

const statusConfig = {
  online: {
    color: 'bg-green-500',
    textColor: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    icon: Wifi,
    label: 'Online'
  },
  offline: {
    color: 'bg-gray-500',
    textColor: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    icon: WifiOff,
    label: 'Offline'
  },
  error: {
    color: 'bg-red-500',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: AlertTriangle,
    label: 'Error'
  }
};

function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 75) return 'text-yellow-600';
  if (score >= 60) return 'text-orange-600';
  return 'text-red-600';
}

function getUsageColor(usage: number): string {
  if (usage >= 90) return 'bg-red-500';
  if (usage >= 75) return 'bg-orange-500';
  if (usage >= 50) return 'bg-yellow-500';
  return 'bg-green-500';
}

export function AgentStatusCard({
  id,
  hostname,
  ip_address,
  os_type,
  os_version,
  status,
  agent_version,
  last_heartbeat,
  cpu_usage,
  memory_usage,
  disk_usage,
  location,
  user,
  tags,
  policy_compliance,
  threat_count,
  last_threat,
  performance_score,
  security_score,
  onConfigure,
  onInvestigate,
  onIsolate
}: AgentStatusCardProps) {
  const config = statusConfig[status];
  const StatusIcon = config.icon;
  
  const complianceScore = policy_compliance ? Object.values(policy_compliance).filter(Boolean).length / Object.values(policy_compliance).length * 100 : 0;

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
              <StatusIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">{hostname}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <Badge className={`${config.textColor} bg-white border-current`}>
                  {config.label}
                </Badge>
                <span className="text-sm text-gray-600">{os_type}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-right">
              <div className={cn('text-lg font-bold', getScoreColor(security_score))}>
                {security_score}
              </div>
              <div className="text-xs text-gray-500">Security</div>
            </div>
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Basic Info */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <span className="text-gray-500">IP Address:</span>
            <span className="ml-2 font-medium">{ip_address}</span>
          </div>
          <div>
            <span className="text-gray-500">Version:</span>
            <span className="ml-2 font-medium">{agent_version}</span>
          </div>
          <div>
            <span className="text-gray-500">Location:</span>
            <span className="ml-2 font-medium">{location}</span>
          </div>
          <div>
            <span className="text-gray-500">User:</span>
            <span className="ml-2 font-medium">{user}</span>
          </div>
        </div>

        {/* Resource Usage */}
        {status === 'online' && cpu_usage !== null && (
          <div className="mb-4">
            <div className="text-sm font-medium text-gray-700 mb-2">Resource Usage</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-gray-400" />
                  <span className="text-sm">CPU</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className={cn('h-2 rounded-full', getUsageColor(cpu_usage))}
                      style={{ width: `${cpu_usage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8">{cpu_usage}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MemoryStick className="w-4 h-4 text-gray-400" />
                  <span className="text-sm">Memory</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className={cn('h-2 rounded-full', getUsageColor(memory_usage))}
                      style={{ width: `${memory_usage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8">{memory_usage}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-4 h-4 text-gray-400" />
                  <span className="text-sm">Disk</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className={cn('h-2 rounded-full', getUsageColor(disk_usage))}
                      style={{ width: `${disk_usage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8">{disk_usage}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Policy Compliance */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Policy Compliance</span>
            <span className={cn('text-sm font-medium', getScoreColor(complianceScore))}>
              {Math.round(complianceScore)}%
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(policy_compliance).map(([key, value]) => (
              <div key={key} className="flex items-center space-x-2">
                {value ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                )}
                <span className="text-sm capitalize">{key.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Threat Info */}
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {threat_count} threats detected
              </span>
            </div>
            {last_threat && (
              <span className="text-xs text-gray-500">
                Last: {formatTimeAgo(last_threat)}
              </span>
            )}
          </div>
        </div>

        {/* Tags */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Last Heartbeat */}
        <div className="mb-4 text-sm text-gray-500">
          Last seen: {formatTimeAgo(last_heartbeat)}
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onConfigure}
            className="flex items-center space-x-1"
          >
            <Settings className="w-4 h-4" />
            <span>Configure</span>
          </Button>
          {threat_count > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={onInvestigate}
              className="flex items-center space-x-1"
            >
              <Shield className="w-4 h-4" />
              <span>Investigate</span>
            </Button>
          )}
          {status === 'online' && (
            <Button
              variant="danger"
              size="sm"
              onClick={onIsolate}
              className="flex items-center space-x-1"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Isolate</span>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}