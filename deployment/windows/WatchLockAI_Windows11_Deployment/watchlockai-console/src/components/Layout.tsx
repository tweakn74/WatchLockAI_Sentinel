import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import {
  LayoutDashboard,
  Shield,
  Monitor,
  Search,
  Zap,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  User,
  Bell,
  Package,
  Download
} from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from './ui/Button';
import { Dropdown } from './ui/Dropdown';
import { Badge } from './ui/badge';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Threats', href: '/threats', icon: Shield },
  { name: 'Agents', href: '/agents', icon: Monitor },
  { name: 'Investigations', href: '/investigations', icon: Search },
  { name: 'Responses', href: '/responses', icon: Zap },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Installation', href: '/installation', icon: Download },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Version', href: '/version', icon: Package },
];

export function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { user, profile, signOut } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const userMenuItems = [
    {
      label: 'Profile',
      value: 'profile',
      icon: <User className="w-4 h-4" />,
      onClick: () => navigate('/settings')
    },
    {
      label: 'Sign Out',
      value: 'signout',
      icon: <LogOut className="w-4 h-4" />,
      onClick: handleSignOut
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden" 
          onClick={() => setIsSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">WatchLockAI</span>
          </div>
          <button
            className="lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
                onClick={() => setIsSidebarOpen(false)}
              >
                <Icon className={cn(
                  'w-5 h-5 mr-3',
                  isActive ? 'text-blue-700' : 'text-gray-400'
                )} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User info at bottom */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {profile?.full_name?.[0] || user?.email?.[0]?.toUpperCase()}
              </span>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">
                {profile?.full_name || 'User'}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {profile?.role || 'viewer'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center">
              <button
                className="lg:hidden"
                onClick={() => setIsSidebarOpen(true)}
              >
                <Menu className="w-6 h-6 text-gray-400" />
              </button>
              
              {/* Page title */}
              <h1 className="ml-4 lg:ml-0 text-xl font-semibold text-gray-900">
                {navigation.find(item => item.href === location.pathname)?.name || 'WatchLockAI Console'}
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="relative p-2 text-gray-400 hover:text-gray-600">
                <Bell className="w-5 h-5" />
                <Badge 
                  variant="destructive" 
                  className="absolute -top-1 -right-1 px-1 min-w-0 h-5 text-xs"
                >
                  3
                </Badge>
              </button>

              {/* User menu */}
              <Dropdown
                trigger={
                  <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {profile?.full_name?.[0] || user?.email?.[0]?.toUpperCase()}
                      </span>
                    </div>
                    <div className="hidden md:block text-left">
                      <p className="text-sm font-medium text-gray-900">
                        {profile?.full_name || 'User'}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">
                        {profile?.role || 'viewer'}
                      </p>
                    </div>
                  </button>
                }
                items={userMenuItems}
                align="right"
              />
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}