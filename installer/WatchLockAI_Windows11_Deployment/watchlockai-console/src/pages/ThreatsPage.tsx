import React, { useState } from 'react';
import { useAuth } from '../lib/auth';
import { useThreats, useEdgeFunction } from '../hooks/useSupabaseQuery';
import { 
  Shield, 
  Search, 
  Filter, 
  Download, 
  Eye,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { DataTable } from '../components/ui/DataTable';
import { SearchInput } from '../components/ui/SearchInput';
import { FilterTabs } from '../components/ui/FilterTabs';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/badge';
import { Modal } from '../components/ui/Modal';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusIndicator } from '../components/ui/StatusIndicator';
import { ActionButton } from '../components/ui/ActionButton';
import { formatTimeAgo, getSeverityColor, getMitreTechniqueName } from '../lib/utils';
import { Threat } from '../lib/supabase';

const statusFilters = [
  { id: 'all', label: 'All Threats', color: 'bg-gray-500' },
  { id: 'open', label: 'Open', color: 'bg-red-500' },
  { id: 'investigating', label: 'Investigating', color: 'bg-yellow-500' },
  { id: 'resolved', label: 'Resolved', color: 'bg-green-500' },
  { id: 'false_positive', label: 'False Positive', color: 'bg-gray-500' }
];

export function ThreatsPage() {
  const { profile } = useAuth();
  const [statusFilter, setStatusFilter] = useState('open');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  
  const organizationId = profile?.organization_id;
  const { data: threatsData, isLoading, refetch } = useThreats(
    organizationId || '', 
    statusFilter === 'all' ? undefined : statusFilter
  );
  const updateThreat = useEdgeFunction();

  const threats = threatsData?.threats || [];

  const filteredThreats = (threats || []).filter(threat =>
    threat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    threat.threat_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    threat.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleStatusUpdate = async (threatId: string, newStatus: string) => {
    try {
      await updateThreat.mutateAsync({
        functionName: 'threat-monitor',
        payload: {
          action: 'update_threat_status',
          threat_data: {
            threat_id: threatId,
            status: newStatus,
            organization_id: organizationId
          }
        }
      });
      refetch();
    } catch (error) {
      console.error('Error updating threat status:', error);
    }
  };

  const handleThreatClick = (threat: Threat) => {
    setSelectedThreat(threat);
    setIsDetailModalOpen(true);
  };

  const threatColumns = [
    {
      key: 'severity' as keyof Threat,
      label: 'Severity',
      sortable: true,
      render: (value: string) => (
        <Badge className={getSeverityColor(value)}>
          {value.toUpperCase()}
        </Badge>
      )
    },
    {
      key: 'title' as keyof Threat,
      label: 'Threat',
      sortable: true,
      render: (value: string) => (
        <span className="font-medium text-gray-900 cursor-pointer hover:text-blue-600">
          {value}
        </span>
      )
    },
    {
      key: 'threat_type' as keyof Threat,
      label: 'Type',
      sortable: true
    },
    {
      key: 'agent_id' as keyof Threat,
      label: 'Agent',
      render: (value: string) => (
        <span className="text-sm text-gray-600 font-mono">
          {value.slice(0, 8)}...
        </span>
      )
    },
    {
      key: 'threat_score' as keyof Threat,
      label: 'Score',
      sortable: true,
      render: (value: number) => (
        <span className={`font-medium ${
          value >= 80 ? 'text-red-600' :
          value >= 60 ? 'text-orange-600' :
          value >= 40 ? 'text-yellow-600' :
          'text-green-600'
        }`}>
          {value || 'N/A'}
        </span>
      )
    },
    {
      key: 'first_seen' as keyof Threat,
      label: 'First Seen',
      sortable: true,
      render: (value: string) => formatTimeAgo(value)
    },
    {
      key: 'status' as keyof Threat,
      label: 'Status',
      render: (value: string) => (
        <StatusIndicator 
          status={value as any}
          size="sm"
        />
      )
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Threat Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and respond to security threats across your infrastructure
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="secondary" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="primary" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filter
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <FilterTabs
          options={statusFilters.map(filter => ({
            ...filter,
            count: filter.id === 'all' 
              ? (threats || []).length 
              : (threats || []).filter(t => t.status === filter.id).length
          }))}
          activeFilter={statusFilter}
          onFilterChange={setStatusFilter}
        />
        
        <div className="flex space-x-3">
          <SearchInput
            placeholder="Search threats, types, or descriptions..."
            value={searchQuery}
            onChange={setSearchQuery}
            className="w-80"
          />
        </div>
      </div>

      {/* Threats Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Security Threats</CardTitle>
            <Badge variant="info">
              {filteredThreats.length} of {threats.length} threats
            </Badge>
          </div>
        </CardHeader>
        <CardContent padding="none">
          <DataTable
            data={filteredThreats}
            columns={threatColumns}
            onRowClick={handleThreatClick}
            loading={isLoading}
            emptyMessage="No threats found matching your criteria"
          />
        </CardContent>
      </Card>

      {/* Threat Detail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        title="Threat Details"
        size="xl"
      >
        {selectedThreat && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {selectedThreat.title}
                </h3>
                <div className="flex items-center space-x-4 mt-2">
                  <Badge className={getSeverityColor(selectedThreat.severity)}>
                    {selectedThreat.severity.toUpperCase()}
                  </Badge>
                  <StatusIndicator status={selectedThreat.status as any} />
                  <span className="text-sm text-gray-500">
                    First seen {formatTimeAgo(selectedThreat.first_seen)}
                  </span>
                </div>
              </div>
              <div className="flex space-x-2">
                <ActionButton
                  icon={<Eye className="w-4 h-4" />}
                  label="Investigate"
                  variant="primary"
                  onClick={() => console.log('Start investigation')}
                />
                <ActionButton
                  icon={<CheckCircle className="w-4 h-4" />}
                  label="Resolve"
                  variant="success"
                  onClick={() => handleStatusUpdate(selectedThreat.id, 'resolved')}
                />
                <ActionButton
                  icon={<XCircle className="w-4 h-4" />}
                  label="False Positive"
                  variant="danger"
                  onClick={() => handleStatusUpdate(selectedThreat.id, 'false_positive')}
                />
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Information */}
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Basic Information</h4>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Threat Type</label>
                    <p className="text-sm text-gray-900">{selectedThreat.threat_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Threat Score</label>
                    <p className="text-sm text-gray-900">{selectedThreat.threat_score || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Source IP</label>
                    <p className="text-sm text-gray-900 font-mono">
                      {selectedThreat.source_ip || 'Unknown'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Destination IP</label>
                    <p className="text-sm text-gray-900 font-mono">
                      {selectedThreat.destination_ip || 'Unknown'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Process Information */}
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Process Information</h4>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Process Name</label>
                    <p className="text-sm text-gray-900 font-mono">
                      {selectedThreat.process_name || 'Unknown'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">File Path</label>
                    <p className="text-sm text-gray-900 font-mono break-all">
                      {selectedThreat.file_path || 'Unknown'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">User Account</label>
                    <p className="text-sm text-gray-900">
                      {selectedThreat.user_account || 'Unknown'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Description */}
            {selectedThreat.description && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                  {selectedThreat.description}
                </p>
              </div>
            )}

            {/* MITRE ATT&CK Techniques */}
            {selectedThreat.mitre_techniques.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">MITRE ATT&CK Techniques</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedThreat.mitre_techniques.map((technique, index) => (
                    <Badge key={index} variant="info">
                      {technique} - {getMitreTechniqueName(technique)}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Command Line */}
            {selectedThreat.command_line && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Command Line</h4>
                <p className="text-sm text-gray-900 font-mono bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                  {selectedThreat.command_line}
                </p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}