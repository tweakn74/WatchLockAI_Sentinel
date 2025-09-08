import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { cn } from '../../lib/utils';

interface DropdownItem {
  label: string;
  value: string;
  icon?: React.ReactNode;
  onClick?: () => void;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  className?: string;
}

export function Dropdown({ trigger, items, align = 'left', className }: DropdownProps) {
  return (
    <Menu as="div" className={cn('relative inline-block text-left', className)}>
      <Menu.Button as="div">
        {trigger}
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className={cn(
          'absolute z-10 mt-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none',
          align === 'right' ? 'right-0 origin-top-right' : 'left-0 origin-top-left'
        )}>
          <div className="py-1">
            {(items || []).map((item) => (
              <Menu.Item key={item.value}>
                {({ active }) => (
                  <button
                    onClick={item.onClick}
                    className={cn(
                      'flex w-full items-center px-4 py-2 text-sm',
                      active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                    )}
                  >
                    {item.icon && (
                      <span className="mr-3">{item.icon}</span>
                    )}
                    {item.label}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}