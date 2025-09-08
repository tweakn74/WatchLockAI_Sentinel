import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './lib/auth';
import { LoginPage } from './pages/LoginPage';
import { EnhancedDashboard } from './pages/EnhancedDashboard';
import { EnhancedThreatsPage } from './pages/EnhancedThreatsPage';
import { EnhancedAgentsPage } from './pages/EnhancedAgentsPage';
import { InvestigationsPage } from './pages/InvestigationsPage';
import { ResponsesPage } from './pages/ResponsesPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { VersionPage } from './pages/VersionPage';
import InstallationPage from './pages/InstallationPage';
import { Layout } from './components/Layout';
import { LoadingSpinner } from './components/ui/LoadingSpinner';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
      />
      <Route 
        path="/installation" 
        element={<InstallationPage />} 
      />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <EnhancedDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/threats" 
        element={
          <ProtectedRoute>
            <EnhancedThreatsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/agents" 
        element={
          <ProtectedRoute>
            <EnhancedAgentsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/investigations" 
        element={
          <ProtectedRoute>
            <InvestigationsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/responses" 
        element={
          <ProtectedRoute>
            <ResponsesPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/reports" 
        element={
          <ProtectedRoute>
            <ReportsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/version" 
        element={
          <ProtectedRoute>
            <VersionPage />
          </ProtectedRoute>
        } 
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;