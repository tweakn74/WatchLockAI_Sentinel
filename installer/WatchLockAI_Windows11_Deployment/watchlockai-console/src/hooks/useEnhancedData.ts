import { useState, useEffect } from 'react';

// Enhanced threat data structure
interface EnhancedThreat {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  threat_type: string;
  threat_score: number;
  confidence_score: number;
  first_seen: string;
  last_seen: string;
  agent_id: string;
  organization_id: string;
  source_ip?: string;
  destination_ip?: string;
  process_name?: string;
  file_path?: string;
  user_account?: string;
  command_line?: string;
  mitre_techniques: Array<{
    id: string;
    name: string;
    tactic: string;
  }>;
  kill_chain_phase: string;
  indicators?: {
    iocs: string[];
    file_hashes?: string[];
    network_signatures?: string[];
    behavioral_patterns?: string[];
  };
  forensics?: {
    memory_artifacts: boolean;
    registry_changes: boolean;
    network_logs: boolean;
    file_system_changes: boolean;
  };
  timeline: Array<{
    timestamp: string;
    event: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  affected_assets: string[];
  response_actions: string[];
}

// Enhanced agent data structure
interface EnhancedAgent {
  id: string;
  hostname: string;
  ip_address: string;
  os_type: string;
  os_version: string;
  status: 'online' | 'offline' | 'error';
  agent_version: string;
  last_heartbeat: string;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  organization_id: string;
  deployment_date: string;
  location: string;
  user: string;
  tags: string[];
  policy_compliance: {
    antimalware: boolean;
    firewall: boolean;
    encryption: boolean;
    patching: boolean;
  };
  threat_count: number;
  last_threat?: string;
  performance_score: number;
  security_score: number;
  configuration: {
    real_time_protection: boolean;
    behavior_monitoring: boolean;
    network_monitoring: boolean;
    file_integrity: boolean;
  };
  installed_software: string[];
  network_connections: number;
  processes_monitored: number;
  events_today: number;
}

// Hook for enhanced threats data
export function useEnhancedThreats() {
  const [threats, setThreats] = useState<EnhancedThreat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/enhanced-threats.json');
        if (!response.ok) {
          throw new Error('Failed to fetch threats data');
        }
        const data = await response.json();
        setThreats(data.threats || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching enhanced threats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchThreats();
    
    // Refetch every 30 seconds for real-time updates
    const interval = setInterval(fetchThreats, 30000);
    return () => clearInterval(interval);
  }, []);

  return { threats, loading, error, refetch: () => setLoading(true) };
}

// Hook for enhanced agents data
export function useEnhancedAgents() {
  const [agents, setAgents] = useState<EnhancedAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/enhanced-agents.json');
        if (!response.ok) {
          throw new Error('Failed to fetch agents data');
        }
        const data = await response.json();
        setAgents(data.agents || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching enhanced agents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
    
    // Refetch every 60 seconds for real-time updates
    const interval = setInterval(fetchAgents, 60000);
    return () => clearInterval(interval);
  }, []);

  return { agents, loading, error, refetch: () => setLoading(true) };
}

// Hook for MITRE ATT&CK data
export function useMitreAttackData() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMitreData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/mitre-attack-data.json');
        if (!response.ok) {
          throw new Error('Failed to fetch MITRE ATT&CK data');
        }
        const mitreData = await response.json();
        setData(mitreData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching MITRE data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMitreData();
  }, []);

  return { data, loading, error };
}

// Hook for security metrics
export function useSecurityMetrics(timeRange: '1h' | '24h' | '7d' | '30d' = '24h') {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const generateMetrics = () => {
      try {
        setLoading(true);
        
        // Generate sample security metrics based on timeRange
        const sampleMetrics = [
          {
            id: 'threat-detection',
            title: 'Threat Detection Rate',
            value: '98.2%',
            change: {
              value: 2.1,
              period: 'vs previous period',
              isPositive: true
            },
            status: 'good',
            description: 'Percentage of threats successfully detected',
            trend: Array.from({ length: 12 }, (_, i) => ({
              time: `${i * 2}h`,
              value: 95 + Math.random() * 5
            }))
          },
          {
            id: 'response-time',
            title: 'Mean Response Time',
            value: '4.2m',
            change: {
              value: 15,
              period: 'improvement',
              isPositive: true
            },
            status: 'good',
            description: 'Average time to respond to critical threats',
            trend: Array.from({ length: 12 }, (_, i) => ({
              time: `${i * 2}h`,
              value: 3 + Math.random() * 2
            }))
          },
          {
            id: 'coverage',
            title: 'MITRE Coverage',
            value: '87%',
            change: {
              value: 3,
              period: 'vs last month',
              isPositive: true
            },
            status: 'warning',
            description: 'Coverage of MITRE ATT&CK techniques',
            trend: Array.from({ length: 12 }, (_, i) => ({
              time: `${i * 2}h`,
              value: 85 + Math.random() * 5
            }))
          },
          {
            id: 'performance',
            title: 'System Performance',
            value: '92%',
            change: {
              value: 1.2,
              period: 'vs baseline',
              isPositive: true
            },
            status: 'good',
            description: 'Overall system performance score',
            trend: Array.from({ length: 12 }, (_, i) => ({
              time: `${i * 2}h`,
              value: 90 + Math.random() * 5
            }))
          }
        ];
        
        setMetrics(sampleMetrics);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error generating security metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    generateMetrics();
    
    // Refresh metrics every 30 seconds
    const interval = setInterval(generateMetrics, 30000);
    return () => clearInterval(interval);
  }, [timeRange]);

  return { metrics, loading, error };
}

// Hook for real-time threat analytics
export function useRealTimeThreatAnalytics() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const generateAnalytics = () => {
      const now = new Date();
      const analytics = {
        threatTrends: Array.from({ length: 24 }, (_, i) => ({
          time: new Date(now.getTime() - (23 - i) * 60 * 60 * 1000).toISOString(),
          threats: Math.floor(Math.random() * 10) + 5,
          critical: Math.floor(Math.random() * 3),
          high: Math.floor(Math.random() * 5) + 2
        })),
        
        severityDistribution: [
          { name: 'Critical', value: 2, fill: '#ef4444' },
          { name: 'High', value: 5, fill: '#f97316' },
          { name: 'Medium', value: 8, fill: '#eab308' },
          { name: 'Low', value: 3, fill: '#3b82f6' }
        ],
        
        topThreatTypes: [
          { type: 'Malware', count: 12, change: 5 },
          { type: 'Phishing', count: 8, change: -2 },
          { type: 'Command & Control', count: 6, change: 3 },
          { type: 'Data Exfiltration', count: 4, change: 1 }
        ],
        
        mitreHeatmap: [
          { technique: 'T1059.001', count: 8, name: 'PowerShell' },
          { technique: 'T1105', count: 6, name: 'Ingress Tool Transfer' },
          { technique: 'T1486', count: 4, name: 'Data Encrypted for Impact' },
          { technique: 'T1003.001', count: 3, name: 'LSASS Memory' }
        ]
      };
      
      setAnalytics(analytics);
      setLoading(false);
    };
    
    generateAnalytics();
    
    // Update analytics every 2 minutes
    const interval = setInterval(generateAnalytics, 120000);
    return () => clearInterval(interval);
  }, []);
  
  return { analytics, loading };
}

// Hook for agent fleet metrics
export function useAgentFleetMetrics() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const generateMetrics = () => {
      const metrics = {
        total: 156,
        online: 142,
        offline: 12,
        error: 2,
        avgCpuUsage: 23.4,
        avgMemoryUsage: 58.2,
        avgDiskUsage: 67.8,
        complianceScore: 89.5,
        
        osDistribution: [
          { name: 'Windows 11', count: 89 },
          { name: 'Windows 10', count: 45 },
          { name: 'Windows Server', count: 18 },
          { name: 'Linux', count: 4 }
        ],
        
        locationDistribution: [
          { location: 'Headquarters', count: 78 },
          { location: 'Remote Workers', count: 45 },
          { location: 'Branch Offices', count: 23 },
          { location: 'Data Centers', count: 10 }
        ],
        
        policyCompliance: {
          antimalware: 95.5,
          firewall: 98.2,
          encryption: 87.3,
          patching: 76.8
        }
      };
      
      setMetrics(metrics);
      setLoading(false);
    };
    
    generateMetrics();
    
    // Update metrics every minute
    const interval = setInterval(generateMetrics, 60000);
    return () => clearInterval(interval);
  }, []);
  
  return { metrics, loading };
}