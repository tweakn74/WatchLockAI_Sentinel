import React from 'react';
import { cn } from '../../lib/utils';
import { formatTimeAgo } from '../../lib/utils';

interface TimelineItemProps {
  timestamp: string;
  title: string;
  description?: string;
  user?: string;
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'gray';
  isLast?: boolean;
  className?: string;
}

export function TimelineItem({
  timestamp,
  title,
  description,
  user,
  icon,
  color = 'blue',
  isLast = false,
  className
}: TimelineItemProps) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    gray: 'bg-gray-500'
  };

  return (
    <div className={cn('relative flex', className)}>
      {/* Timeline line */}
      {!isLast && (
        <div className="absolute left-4 top-8 w-0.5 h-full bg-gray-200" />
      )}
      
      {/* Icon */}
      <div className={cn(
        'flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0',
        colorClasses[color]
      )}>
        {icon ? (
          <div className="text-white text-xs">{icon}</div>
        ) : (
          <div className="w-2 h-2 bg-white rounded-full" />
        )}
      </div>
      
      {/* Content */}
      <div className="ml-4 flex-1 pb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className="text-sm font-medium text-gray-900">{title}</h4>
            {description && (
              <p className="text-sm text-gray-600 mt-1">{description}</p>
            )}
            {user && (
              <p className="text-xs text-gray-500 mt-1">by {user}</p>
            )}
          </div>
          <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
            {formatTimeAgo(timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
}