import React from 'react';
import { cn } from '../../lib/utils';

interface FilterOption {
  id: string;
  label: string;
  count?: number;
  color?: string;
}

interface FilterTabsProps {
  options: FilterOption[];
  activeFilter: string;
  onFilterChange: (filterId: string) => void;
  className?: string;
}

export function FilterTabs({ options, activeFilter, onFilterChange, className }: FilterTabsProps) {
  return (
    <div className={cn('flex space-x-1 bg-gray-100 p-1 rounded-lg', className)}>
      {(options || []).map((option) => (
        <button
          key={option.id}
          onClick={() => onFilterChange(option.id)}
          className={cn(
            'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
            activeFilter === option.id
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          )}
        >
          {option.color && (
            <div 
              className={cn('w-2 h-2 rounded-full mr-2', option.color)}
            />
          )}
          <span>{option.label}</span>
          {option.count !== undefined && (
            <span className={cn(
              'ml-2 px-2 py-0.5 text-xs rounded-full',
              activeFilter === option.id
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-200 text-gray-600'
            )}>
              {option.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}