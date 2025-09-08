import React from 'react';
import { cn } from '../../lib/utils';

interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function Switch({ 
  checked, 
  onChange, 
  disabled = false, 
  size = 'md',
  className 
}: SwitchProps) {
  const sizeClasses = {
    sm: 'h-5 w-9',
    md: 'h-6 w-11'
  };

  const thumbSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5'
  };

  const thumbTranslateClasses = {
    sm: checked ? 'translate-x-4' : 'translate-x-0',
    md: checked ? 'translate-x-5' : 'translate-x-0'
  };

  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative inline-flex shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        checked ? 'bg-blue-600' : 'bg-gray-200',
        disabled && 'opacity-50 cursor-not-allowed',
        sizeClasses[size],
        className
      )}
    >
      <span
        className={cn(
          'pointer-events-none relative inline-block rounded-full bg-white shadow transform ring-0 transition duration-200 ease-in-out',
          thumbSizeClasses[size],
          thumbTranslateClasses[size]
        )}
      />
    </button>
  );
}