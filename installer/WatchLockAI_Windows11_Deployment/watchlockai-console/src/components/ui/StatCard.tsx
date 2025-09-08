import React from 'react';
import { cn } from '../../lib/utils';
import { Card } from './Card';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'gray';
  className?: string;
}

export function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  color = 'blue',
  className 
}: StatCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    red: 'text-red-600 bg-red-50',
    gray: 'text-gray-600 bg-gray-50'
  };

  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={cn(
              'flex items-center mt-2 text-sm',
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            )}>
              <span className={cn(
                'inline-block w-0 h-0 mr-1',
                trend.isPositive 
                  ? 'border-l-2 border-r-2 border-b-2 border-transparent border-b-green-600'
                  : 'border-l-2 border-r-2 border-t-2 border-transparent border-t-red-600'
              )} />
              {Math.abs(trend.value)}%
            </div>
          )}
        </div>
        {icon && (
          <div className={cn(
            'flex items-center justify-center w-12 h-12 rounded-lg',
            colorClasses[color]
          )}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}