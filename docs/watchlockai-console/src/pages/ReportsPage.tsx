import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

export function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Security Reports & Analytics</h1>
        <p className="text-gray-600 mt-1">
          Generate comprehensive security reports and analyze threat trends
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Report Generation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Report generation features coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
}