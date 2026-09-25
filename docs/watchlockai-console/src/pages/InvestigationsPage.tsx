import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

export function InvestigationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Investigation Management</h1>
        <p className="text-gray-600 mt-1">
          Manage security investigations and forensic analysis cases
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Investigation Cases</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Investigation management features coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
}