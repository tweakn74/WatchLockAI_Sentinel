import React, { useState } from 'react';
import { useAuth } from '../lib/auth';
import { Shield, Eye, EyeOff } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Alert } from '../components/ui/Alert';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setError('');

    try {
      await signIn(email, password);
    } catch (err: any) {
      setError(err.message || 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center">
                <Shield className="w-10 h-10 text-white" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              WatchLockAI Console
            </h2>
            <p className="text-gray-600">
              Enterprise Cybersecurity Management Platform
            </p>
          </div>

          {error && (
            <Alert variant="error" className="mb-6">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              Sign In to Console
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Secure access to your organization's security operations center
            </p>
          </div>

          {/* Demo Access */}
          <div className="mt-8 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="text-sm font-medium text-green-900 mb-2">🚀 Demo Access Available</h3>
            <div className="text-xs text-green-800 space-y-1">
              <p><strong>Email:</strong> demo@demo.com</p>
              <p><strong>Password:</strong> demo123</p>
              <p className="mt-2 text-green-600">
                <strong>Full Enterprise Features:</strong> Real-time threat monitoring, agent management, MITRE ATT&CK mapping, forensics investigation, and analytics dashboard.
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setEmail('demo@demo.com');
                setPassword('demo123');
              }}
              className="mt-3 text-xs bg-green-100 hover:bg-green-200 text-green-800 px-3 py-1 rounded-md transition-colors"
            >
              Auto-fill Demo Credentials
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}