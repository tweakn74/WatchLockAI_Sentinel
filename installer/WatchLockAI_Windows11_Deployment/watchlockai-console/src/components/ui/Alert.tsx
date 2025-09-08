import React from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error' | 'destructive';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const variantConfig = {
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon: 'text-blue-400',
    title: 'text-blue-800',
    text: 'text-blue-700',
    iconComponent: Info
  },
  success: {
    container: 'bg-green-50 border-green-200',
    icon: 'text-green-400',
    title: 'text-green-800',
    text: 'text-green-700',
    iconComponent: CheckCircle
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200',
    icon: 'text-yellow-400',
    title: 'text-yellow-800',
    text: 'text-yellow-700',
    iconComponent: AlertTriangle
  },
  error: {
    container: 'bg-red-50 border-red-200',
    icon: 'text-red-400',
    title: 'text-red-800',
    text: 'text-red-700',
    iconComponent: XCircle
  },
  destructive: {
    container: 'bg-red-50 border-red-200',
    icon: 'text-red-400',
    title: 'text-red-800',
    text: 'text-red-700',
    iconComponent: XCircle
  }
};

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const config = variantConfig[variant];
  const IconComponent = config.iconComponent;

  return (
    <div className={cn(
      'border rounded-lg p-4',
      config.container,
      className
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <IconComponent className={cn('h-5 w-5', config.icon)} />
        </div>
        <div className="ml-3">
          {title && (
            <h3 className={cn('text-sm font-medium', config.title)}>
              {title}
            </h3>
          )}
          <div className={cn('text-sm', title ? 'mt-2' : '', config.text)}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}