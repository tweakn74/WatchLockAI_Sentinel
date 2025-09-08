import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Badge } from './badge';
import { 
  Shield, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Target,
  Activity
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface SecurityMetric {
  id: string;
  title: string;
  value: string | number;
  change?: {
    value: number;
    period: string;
    isPositive: boolean;
  };
  trend?: Array<{ time: string; value: number }>;
  status?: 'good' | 'warning' | 'critical';
  description?: string;
}

interface SecurityMetricsProps {
  metrics: SecurityMetric[];
  timeRange: '1h' | '24h' | '7d' | '30d';
  onTimeRangeChange?: (range: '1h' | '24h' | '7d' | '30d') => void;
  className?: string;
}

const statusConfig = {
  good: {
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200'
  },
  critical: {
    icon: AlertTriangle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  }
};

const metricIcons = {
  'threat-detection': Shield,
  'response-time': Clock,
  'coverage': Target,
  'performance': Activity,
  'default': TrendingUp
};

export function SecurityMetrics({
  metrics,
  timeRange,
  onTimeRangeChange,
  className
}: SecurityMetricsProps) {
  const getMetricIcon = (metricId: string) => {
    return metricIcons[metricId as keyof typeof metricIcons] || metricIcons.default;
  };

  const timeRangeOptions = [
    { value: '1h', label: '1 Hour' },
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' }
  ];

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Security Metrics</h2>
          <p className="text-sm text-gray-600">Real-time security posture and performance indicators</p>
        </div>
        
        {/* Time Range Selector */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {timeRangeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onTimeRangeChange?.(option.value as any)}
              className={cn(
                'px-3 py-1 text-sm rounded-md transition-colors',
                timeRange === option.value
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => {
          const MetricIcon = getMetricIcon(metric.id);
          const status = metric.status || 'good';
          const config = statusConfig[status];
          const StatusIcon = config.icon;

          return (
            <Card 
              key={metric.id}
              className={cn(
                'hover:shadow-md transition-shadow',
                metric.status && metric.status !== 'good' ? config.borderColor : ''
              )}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {metric.title}
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <MetricIcon className="w-4 h-4 text-gray-400" />
                  {metric.status && metric.status !== 'good' && (
                    <StatusIcon className={cn('w-4 h-4', config.color)} />
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="flex items-baseline space-x-2">
                  <div className="text-2xl font-bold text-gray-900">
                    {metric.value}
                  </div>
                  
                  {metric.change && (
                    <div className={cn(
                      'flex items-center space-x-1 text-sm',
                      metric.change.isPositive ? 'text-green-600' : 'text-red-600'
                    )}>
                      {metric.change.isPositive ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      <span>{Math.abs(metric.change.value)}%</span>
                    </div>
                  )}
                </div>
                
                {metric.change && (
                  <p className="text-xs text-gray-500 mt-1">
                    {metric.change.period}
                  </p>
                )}
                
                {metric.description && (
                  <p className="text-xs text-gray-600 mt-2">
                    {metric.description}
                  </p>
                )}
                
                {/* Mini trend chart */}
                {metric.trend && metric.trend.length > 0 && (
                  <div className="mt-3 h-12">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={metric.trend}>
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke={metric.status === 'critical' ? '#ef4444' : 
                                 metric.status === 'warning' ? '#f59e0b' : '#10b981'}
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Additional Status Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Security Score */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Security Posture Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="2"
                  />
                  <path
                    d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                    strokeDasharray="85, 100"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-900">85%</span>
                </div>
              </div>
            </div>
            <div className="text-center mt-4">
              <Badge className="bg-green-100 text-green-800">
                Good Security Posture
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Threat Level Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Threat Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Critical', value: 2, fill: '#ef4444' },
                      { name: 'High', value: 4, fill: '#f97316' },
                      { name: 'Medium', value: 8, fill: '#eab308' },
                      { name: 'Low', value: 3, fill: '#3b82f6' }
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={50}
                    paddingAngle={2}
                    dataKey="value"
                  />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full" />
                <span>Critical (2)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full" />
                <span>High (4)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                <span>Medium (8)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full" />
                <span>Low (3)</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detection Coverage */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">MITRE ATT&CK Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { tactic: 'Initial Access', coverage: 92 },
                { tactic: 'Execution', coverage: 88 },
                { tactic: 'Persistence', coverage: 95 },
                { tactic: 'Credential Access', coverage: 78 }
              ].map((item) => (
                <div key={item.tactic}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.tactic}</span>
                    <span className="font-medium">{item.coverage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={cn(
                        'h-2 rounded-full',
                        item.coverage >= 90 ? 'bg-green-500' :
                        item.coverage >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                      )}
                      style={{ width: `${item.coverage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}