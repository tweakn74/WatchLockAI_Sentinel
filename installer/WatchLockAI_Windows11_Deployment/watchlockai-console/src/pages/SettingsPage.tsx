import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Manage your account preferences and organization settings
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Settings configuration coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
}