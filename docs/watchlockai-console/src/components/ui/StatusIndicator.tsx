import React from 'react';
import { cn } from '../../lib/utils';

type Status = 'online' | 'offline' | 'warning' | 'error' | 'success' | 'pending';

interface StatusIndicatorProps {
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const statusConfig = {
  online: {
    color: 'bg-green-500',
    label: 'Online'
  },
  offline: {
    color: 'bg-gray-400',
    label: 'Offline'
  },
  warning: {
    color: 'bg-yellow-500',
    label: 'Warning'
  },
  error: {
    color: 'bg-red-500',
    label: 'Error'
  },
  success: {
    color: 'bg-green-500',
    label: 'Success'
  },
  pending: {
    color: 'bg-blue-500',
    label: 'Pending'
  }
};

const sizeConfig = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4'
};

export function StatusIndicator({ 
  status, 
  size = 'md', 
  showLabel = true, 
  className 
}: StatusIndicatorProps) {
  const config = statusConfig[status] || statusConfig.offline; // Default to offline if status not found
  
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <div className={cn(
        'rounded-full flex-shrink-0',
        config.color,
        sizeConfig[size]
      )} />
      {showLabel && (
        <span className="text-sm text-gray-700 capitalize">
          {config.label}
        </span>
      )}
    </div>
  );
}