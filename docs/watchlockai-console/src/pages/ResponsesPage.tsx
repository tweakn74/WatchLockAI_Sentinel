import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

export function ResponsesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Incident Response</h1>
        <p className="text-gray-600 mt-1">
          Automated and manual response actions for security incidents
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Response Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Incident response features coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
}