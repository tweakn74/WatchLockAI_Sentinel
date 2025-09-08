import React from 'react';
import { cn } from '../../lib/utils';
import { Card } from './Card';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    period: string;
    isPositive?: boolean;
  };
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';
  format?: 'number' | 'currency' | 'percentage';
  className?: string;
}

export function MetricCard({ 
  title, 
  value, 
  change, 
  icon, 
  color = 'blue',
  format = 'number',
  className 
}: MetricCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50 border-blue-100',
    green: 'text-green-600 bg-green-50 border-green-100',
    yellow: 'text-yellow-600 bg-yellow-50 border-yellow-100',
    red: 'text-red-600 bg-red-50 border-red-100',
    purple: 'text-purple-600 bg-purple-50 border-purple-100',
    gray: 'text-gray-600 bg-gray-50 border-gray-100'
  };

  const formatValue = (val: string | number) => {
    const numVal = typeof val === 'string' ? parseFloat(val) : val;
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', { 
          style: 'currency', 
          currency: 'USD',
          minimumFractionDigits: 0
        }).format(numVal);
      case 'percentage':
        return `${numVal}%`;
      default:
        return typeof val === 'number' 
          ? new Intl.NumberFormat('en-US').format(val)
          : val;
    }
  };

  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">
            {formatValue(value)}
          </p>
          {change && (
            <div className="flex items-center mt-2">
              <div className={cn(
                'flex items-center text-sm font-medium',
                change.isPositive !== false ? 'text-green-600' : 'text-red-600'
              )}>
                {change.isPositive !== false ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
                )}
                {Math.abs(change.value)}%
              </div>
              <span className="text-sm text-gray-500 ml-2">
                {change.period}
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={cn(
            'flex items-center justify-center w-12 h-12 rounded-lg border',
            colorClasses[color]
          )}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}