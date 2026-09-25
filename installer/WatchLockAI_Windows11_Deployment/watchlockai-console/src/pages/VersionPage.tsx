import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Download, 
  RotateCcw, 
  Shield, 
  Info, 
  CheckCircle, 
  AlertTriangle,
  History,
  Package
} from 'lucide-react';

interface VersionInfo {
  version: string;
  build: string;
  name: string;
  date: string;
  description: string;
}

interface VersionHistory {
  version: string;
  build: string;
  name: string;
  date: string;
  description: string;
  changes: string[];
  rollback_available: boolean;
  backup_path?: string;
}

interface ComponentVersion {
  version: string;
  last_updated: string;
  status: 'stable' | 'new' | 'enhanced' | 'deprecated';
}

interface VersionData {
  current: VersionInfo;
  history: VersionHistory[];
  components: Record<string, ComponentVersion>;
  metadata: {
    author: string;
    product: string;
    platform: string;
    architecture: string;
    dotnet_version: string;
    powershell_version: string;
    install_type: string;
    license: string;
  };
}

interface Backup {
  backup_id: string;
  source_version: string;
  created_date: string;
  description: string;
  files_count: number;
}

export const VersionPage: React.FC = () => {
  const [versionData, setVersionData] = useState<VersionData | null>(null);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rollbackInProgress, setRollbackInProgress] = useState(false);

  useEffect(() => {
    loadVersionData();
    loadBackups();
  }, []);

  const loadVersionData = async () => {
    try {
      setLoading(true);
      // In a real application, this would fetch from an API
      // For now, we'll simulate the VERSION.json structure
      const mockVersionData: VersionData = {
        current: {
          version: "1.2.0",
          build: "20250712.010722",
          name: "Professional Integration Update",
          date: "2025-07-12T01:07:22Z",
          description: "Added system tray application, enhanced system updater (7 tests), Add/Remove Programs registration, and professional versioning system"
        },
        history: [
          {
            version: "1.1.0",
            build: "20250710.000000",
            name: "System Tray & Enhanced Diagnostics",
            date: "2025-07-10T00:00:00Z",
            description: "Added system tray application with real-time monitoring and enhanced system updater with 7 diagnostic categories",
            changes: [
              "System tray application with green/red status indicators",
              "Enhanced system updater (7 tests vs previous 5-6)",
              "Add/Remove Programs registration testing and repair",
              "Professional uninstaller with complete cleanup",
              "Event source registration for system tray logging"
            ],
            rollback_available: true,
            backup_path: "backups/v1.1.0"
          },
          {
            version: "1.0.0",
            build: "20250708.000000",
            name: "Initial Release",
            date: "2025-07-08T00:00:00Z",
            description: "Initial WatchLockAI release with core security monitoring, web console, and Windows 11 integration",
            changes: [
              "Core WatchLockAI service and monitoring engine",
              "Web-based management console",
              "Basic system updater and diagnostic tools",
              "Windows 11 security integration",
              "Basic installation and configuration system"
            ],
            rollback_available: true,
            backup_path: "backups/v1.0.0"
          }
        ],
        components: {
          core_service: {
            version: "1.0.0",
            last_updated: "2025-07-08T00:00:00Z",
            status: "stable"
          },
          web_console: {
            version: "1.0.0",
            last_updated: "2025-07-08T00:00:00Z",
            status: "stable"
          },
          system_tray: {
            version: "1.2.0",
            last_updated: "2025-07-12T01:07:22Z",
            status: "new"
          },
          system_updater: {
            version: "1.2.0",
            last_updated: "2025-07-12T01:07:22Z",
            status: "enhanced"
          },
          add_remove_programs: {
            version: "1.2.0",
            last_updated: "2025-07-12T01:07:22Z",
            status: "new"
          },
          versioning_system: {
            version: "1.2.0",
            last_updated: "2025-07-12T01:07:22Z",
            status: "new"
          }
        },
        metadata: {
          author: "MiniMax Agent",
          product: "WatchLockAI Security Suite",
          platform: "Windows 11",
          architecture: "x64",
          dotnet_version: "8.0",
          powershell_version: "5.1+",
          install_type: "Enterprise",
          license: "Commercial"
        }
      };
      
      setVersionData(mockVersionData);
    } catch (err) {
      setError('Failed to load version information');
      console.error('Error loading version data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadBackups = async () => {
    try {
      // Mock backup data
      const mockBackups: Backup[] = [
        {
          backup_id: "Manual_20250712_010500",
          source_version: "1.2.0",
          created_date: "2025-07-12T01:05:00Z",
          description: "Manual backup before rollback testing",
          files_count: 8
        },
        {
          backup_id: "PreInstall_20250710_000000",
          source_version: "1.1.0",
          created_date: "2025-07-10T00:00:00Z",
          description: "Automatic backup before version 1.2.0 installation",
          files_count: 6
        }
      ];
      
      setBackups(mockBackups);
    } catch (err) {
      console.error('Error loading backups:', err);
    }
  };

  const handleRollback = async (targetVersion: string) => {
    if (!confirm(`Are you sure you want to rollback to version ${targetVersion}? This will restore WatchLockAI to a previous state.`)) {
      return;
    }

    setRollbackInProgress(true);
    try {
      // In a real application, this would call the Version Manager API
      alert(`Rollback to version ${targetVersion} would be initiated. This requires administrator privileges and will be handled by the WatchLockAI Version Manager.`);
    } catch (err) {
      setError('Rollback failed. Please use the Version Manager directly.');
    } finally {
      setRollbackInProgress(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      alert('Backup creation would be initiated via the WatchLockAI Version Manager.');
    } catch (err) {
      setError('Failed to create backup');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      stable: { variant: 'default' as const, color: 'bg-green-100 text-green-800' },
      new: { variant: 'default' as const, color: 'bg-blue-100 text-blue-800' },
      enhanced: { variant: 'default' as const, color: 'bg-purple-100 text-purple-800' },
      deprecated: { variant: 'default' as const, color: 'bg-orange-100 text-orange-800' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.stable;
    
    return (
      <Badge variant={config.variant} className={config.color}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <div>
            <p className="font-medium">Error Loading Version Information</p>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      </div>
    );
  }

  if (!versionData) {
    return (
      <div className="p-6">
        <Alert>
          <Info className="h-4 w-4" />
          <div>
            <p className="font-medium">No Version Information Available</p>
            <p className="text-sm">Version data could not be loaded.</p>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Version Management</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Professional version control with rollback capabilities
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={handleCreateBackup} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Create Backup
          </Button>
        </div>
      </div>

      {/* Current Version Overview */}
      <Card className="p-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Shield className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              WatchLockAI Security Suite v{versionData.current.version}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Build {versionData.current.build} * {versionData.current.name}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Released: {new Date(versionData.current.date).toLocaleDateString()}
            </p>
          </div>
          <div className="text-right">
            <Badge variant="default" className="bg-green-100 text-green-800">
              <CheckCircle className="h-3 w-3 mr-1" />
              Current
            </Badge>
          </div>
        </div>
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {versionData.current.description}
          </p>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="components" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="components">Components</TabsTrigger>
          <TabsTrigger value="history">Version History</TabsTrigger>
          <TabsTrigger value="backups">Backups</TabsTrigger>
          <TabsTrigger value="metadata">System Info</TabsTrigger>
        </TabsList>

        {/* Components Tab */}
        <TabsContent value="components" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Component Versions
            </h3>
            <div className="grid gap-4">
              {Object.entries(versionData.components).map(([componentName, componentData]) => (
                <div
                  key={componentName}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <Package className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {componentName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Last updated: {new Date(componentData.last_updated).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-mono text-gray-600 dark:text-gray-300">
                      v{componentData.version}
                    </span>
                    {getStatusBadge(componentData.status)}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Version History Tab */}
        <TabsContent value="history" className="space-y-4">
          <div className="space-y-4">
            {versionData.history.map((version, index) => (
              <Card key={version.version} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <History className="h-5 w-5 text-gray-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Version {version.version} - {version.name}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Build {version.build} * Released {new Date(version.date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {version.rollback_available && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRollback(version.version)}
                        disabled={rollbackInProgress}
                      >
                        <RotateCcw className="h-4 w-4 mr-2" />
                        Rollback
                      </Button>
                    )}
                    <Badge variant={version.rollback_available ? "default" : "secondary"}>
                      {version.rollback_available ? "Rollback Available" : "No Backup"}
                    </Badge>
                  </div>
                </div>
                
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {version.description}
                </p>
                
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Changes:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    {version.changes.map((change, changeIndex) => (
                      <li key={changeIndex}>{change}</li>
                    ))}
                  </ul>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Backups Tab */}
        <TabsContent value="backups" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Available Backups
            </h3>
            {backups.length === 0 ? (
              <div className="text-center py-8">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">No backups available</p>
              </div>
            ) : (
              <div className="space-y-4">
                {backups.map((backup) => (
                  <div
                    key={backup.backup_id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <Download className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {backup.backup_id}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Version {backup.source_version} * {backup.files_count} files
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {backup.description}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(backup.created_date).toLocaleDateString()}
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRollback(backup.source_version)}
                        disabled={rollbackInProgress}
                        className="mt-2"
                      >
                        <RotateCcw className="h-4 w-4 mr-2" />
                        Restore
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        {/* System Metadata Tab */}
        <TabsContent value="metadata" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              System Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(versionData.metadata).map(([key, value]) => (
                <div key={key} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                  <p className="font-medium text-gray-900 dark:text-white">{value}</p>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Version Manager Notice */}
      <Alert>
        <Info className="h-4 w-4" />
        <div>
          <p className="font-medium">Professional Version Management</p>
          <p className="text-sm">
            Advanced version operations require administrator privileges and are handled by the 
            WatchLockAI Version Manager. Check the system tray for quick access to version controls.
          </p>
        </div>
      </Alert>
    </div>
  );
};

export default VersionPage;
