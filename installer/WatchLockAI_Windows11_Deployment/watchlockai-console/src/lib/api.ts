import { supabase } from './supabase';

// API Configuration
const API_CONFIG = {
  // Set to true when Supabase is properly configured
  useSupabase: false,
  // Service role key for backend operations (when available)
  serviceRoleKey: 'e#R6mY0sif&TXvwUdTeWUN%39mWgZJfn',
  // Fallback to local data when backend is unavailable
  fallbackToLocal: true
};

// Check if we can connect to Supabase
let supabaseAvailable = false;

// Test Supabase connection
export async function testSupabaseConnection(): Promise<boolean> {
  try {
    const { data, error } = await supabase.from('organizations').select('count').limit(1);
    supabaseAvailable = !error;
    API_CONFIG.useSupabase = supabaseAvailable;
    return supabaseAvailable;
  } catch (error) {
    console.warn('Supabase connection test failed:', error);
    supabaseAvailable = false;
    API_CONFIG.useSupabase = false;
    return false;
  }
}

// Generic API response type
interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  success: boolean;
}

// Data Models
export interface Organization {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  plan_type: string;
  logo_url?: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  organization_id: string;
  hostname: string;
  ip_address: string;
  agent_version: string;
  os_type: string;
  os_version: string;
  status: 'online' | 'offline' | 'error';
  last_heartbeat: string;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  policy_id?: string;
  configuration: Record<string, any>;
  tags: string[];
  // Extended properties for UI compatibility
  user: string;
  location: string;
  security_score: number;
  performance_score: number;
  policy_compliance: {
    antimalware: boolean;
    firewall: boolean;
    encryption: boolean;
    patching: boolean;
  };
  threat_count: number;
  events_today: number;
  processes_monitored: number;
  last_threat?: string;
  created_at: string;
  updated_at: string;
}

export interface Threat {
  id: string;
  organization_id: string;
  agent_id: string;
  threat_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  title: string;
  description: string;
  mitre_techniques: Array<{ id: string; name: string; tactic: string }>;
  indicators?: {
    iocs: string[];
    file_hashes?: string[];
    network_indicators?: string[];
  };
  affected_assets: string[];
  threat_score: number;
  confidence_score: number;
  kill_chain_phase: string;
  response_actions: string[];
  timeline: Array<{
    timestamp: string;
    event: string;
    details: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
  }>;
  first_seen: string;
  last_seen: string;
  resolved_at?: string;
  // Extended properties for UI compatibility
  hostname?: string;
  created_at: string;
  updated_at: string;
}

export interface Investigation {
  id: string;
  organization_id: string;
  threat_id: string;
  title: string;
  status: 'active' | 'completed' | 'on_hold';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: string;
  findings: Array<{
    timestamp: string;
    finding: string;
    evidence: string;
    analyst: string;
  }>;
  evidence: Array<{
    type: string;
    description: string;
    file_path?: string;
    hash?: string;
  }>;
  created_at: string;
  updated_at: string;
}

// API Service Class
class ApiService {
  constructor() {
    // Test connection on initialization
    this.init();
  }

  private async init() {
    await testSupabaseConnection();
  }

  // Organizations API
  async getOrganizations(): Promise<ApiResponse<Organization[]>> {
    if (API_CONFIG.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('organizations')
          .select('*')
          .order('created_at', { ascending: false });
        
        return {
          data: data || [],
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback to local data
    return this.getLocalOrganizations();
  }

  async createOrganization(org: Partial<Organization>): Promise<ApiResponse<Organization>> {
    if (API_CONFIG.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('organizations')
          .insert(org)
          .select()
          .single();
        
        return {
          data: data,
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback - simulate creation
    const newOrg: Organization = {
      id: `org_${Date.now()}`,
      name: org.name || 'Demo Organization',
      slug: org.slug || 'demo-org',
      domain: org.domain || 'demo.com',
      plan_type: org.plan_type || 'enterprise',
      logo_url: org.logo_url,
      settings: org.settings || {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    return {
      data: newOrg,
      error: null,
      success: true
    };
  }

  // Agents API
  async getAgents(organizationId?: string): Promise<ApiResponse<Agent[]>> {
    if (API_CONFIG.useSupabase) {
      try {
        let query = supabase.from('agents').select('*');
        
        if (organizationId) {
          query = query.eq('organization_id', organizationId);
        }
        
        const { data, error } = await query.order('last_heartbeat', { ascending: false });
        
        return {
          data: data || [],
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback to local data
    return this.getLocalAgents();
  }

  async updateAgentStatus(agentId: string, status: string): Promise<ApiResponse<Agent>> {
    if (API_CONFIG.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('agents')
          .update({ 
            status, 
            last_heartbeat: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .eq('id', agentId)
          .select()
          .single();
        
        return {
          data: data,
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback - simulate update
    return {
      data: null,
      error: null,
      success: true
    };
  }

  // Threats API
  async getThreats(organizationId?: string): Promise<ApiResponse<Threat[]>> {
    if (API_CONFIG.useSupabase) {
      try {
        let query = supabase.from('threats').select('*');
        
        if (organizationId) {
          query = query.eq('organization_id', organizationId);
        }
        
        const { data, error } = await query.order('first_seen', { ascending: false });
        
        return {
          data: data || [],
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback to local data
    return this.getLocalThreats();
  }

  async updateThreatStatus(threatId: string, status: string): Promise<ApiResponse<Threat>> {
    if (API_CONFIG.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('threats')
          .update({ 
            status,
            updated_at: new Date().toISOString(),
            ...(status === 'resolved' && { resolved_at: new Date().toISOString() })
          })
          .eq('id', threatId)
          .select()
          .single();
        
        return {
          data: data,
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback - simulate update
    return {
      data: null,
      error: null,
      success: true
    };
  }

  async createThreat(threat: Partial<Threat>): Promise<ApiResponse<Threat>> {
    if (API_CONFIG.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('threats')
          .insert(threat)
          .select()
          .single();
        
        return {
          data: data,
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback - simulate creation
    const newThreat: Threat = {
      id: `threat_${Date.now()}`,
      organization_id: threat.organization_id || 'demo-org',
      agent_id: threat.agent_id || 'demo-agent',
      threat_type: threat.threat_type || 'Unknown',
      severity: threat.severity || 'medium',
      status: threat.status || 'open',
      title: threat.title || 'New Threat',
      description: threat.description || '',
      mitre_techniques: threat.mitre_techniques || [],
      indicators: threat.indicators || { iocs: [], file_hashes: [], network_indicators: [] },
      affected_assets: threat.affected_assets || [],
      threat_score: threat.threat_score || 50,
      confidence_score: threat.confidence_score || 0.5,
      kill_chain_phase: threat.kill_chain_phase,
      response_actions: threat.response_actions || [],
      timeline: threat.timeline || [],
      first_seen: new Date().toISOString(),
      last_seen: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    return {
      data: newThreat,
      error: null,
      success: true
    };
  }

  // Investigations API
  async getInvestigations(organizationId?: string): Promise<ApiResponse<Investigation[]>> {
    if (API_CONFIG.useSupabase) {
      try {
        let query = supabase.from('investigations').select('*');
        
        if (organizationId) {
          query = query.eq('organization_id', organizationId);
        }
        
        const { data, error } = await query.order('created_at', { ascending: false });
        
        return {
          data: data || [],
          error: error?.message || null,
          success: !error
        };
      } catch (error: any) {
        return this.handleError(error);
      }
    }
    
    // Fallback to local data
    return this.getLocalInvestigations();
  }

  // Utility methods
  private handleError(error: any): ApiResponse<any> {
    console.error('API Error:', error);
    return {
      data: null,
      error: error.message || 'An unknown error occurred',
      success: false
    };
  }

  // Local data fallbacks (using the existing enhanced data)
  private async getLocalOrganizations(): Promise<ApiResponse<Organization[]>> {
    const orgs: Organization[] = [
      {
        id: 'org_demo_001',
        name: 'Acme Corporation',
        slug: 'acme-corp',
        domain: 'acme.com',
        plan_type: 'enterprise',
        logo_url: null,
        settings: {
          timezone: 'UTC',
          retention_days: 90,
          alert_threshold: 'medium'
        },
        created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date().toISOString()
      }
    ];
    
    return {
      data: orgs,
      error: null,
      success: true
    };
  }

  private async getLocalAgents(): Promise<ApiResponse<Agent[]>> {
    try {
      const response = await fetch('/data/enhanced-agents.json');
      const agents = await response.json();
      return {
        data: agents,
        error: null,
        success: true
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  private async getLocalThreats(): Promise<ApiResponse<Threat[]>> {
    try {
      const response = await fetch('/data/enhanced-threats.json');
      const threats = await response.json();
      return {
        data: threats,
        error: null,
        success: true
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  private async getLocalInvestigations(): Promise<ApiResponse<Investigation[]>> {
    const investigations: Investigation[] = [
      {
        id: 'inv_001',
        organization_id: 'org_demo_001',
        threat_id: 'threat_001',
        title: 'PowerShell Malware Investigation',
        status: 'active',
        priority: 'high',
        assigned_to: 'analyst_001',
        findings: [
          {
            timestamp: new Date().toISOString(),
            finding: 'Malicious PowerShell script identified',
            evidence: 'Script hash: abc123...',
            analyst: 'Security Analyst'
          }
        ],
        evidence: [
          {
            type: 'file',
            description: 'Malicious PowerShell script',
            file_path: 'C:\\temp\\malware.ps1',
            hash: 'abc123def456'
          }
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];
    
    return {
      data: investigations,
      error: null,
      success: true
    };
  }

  // Check API health
  async healthCheck(): Promise<{ supabase: boolean; local: boolean }> {
    const supabaseHealth = await testSupabaseConnection();
    return {
      supabase: supabaseHealth,
      local: true
    };
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;