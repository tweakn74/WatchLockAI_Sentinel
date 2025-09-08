import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://iozahbnaeaccvjyjljmv.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlvemFoYm5hZWFjY3ZqeWpsam12Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE5Mzk3OTUsImV4cCI6MjA2NzUxNTc5NX0.GMkiSmGJRJcMYqQIVbYdLH1mi9dti5dZLqs_i1QvZT8';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types
export interface Organization {
  id: string;
  name: string;
  subdomain: string;
  logo_url?: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  organization_id: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'analyst' | 'viewer';
  permissions: string[];
  avatar_url?: string;
  last_login_at?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  organization_id: string;
  hostname: string;
  ip_address?: string;
  agent_version?: string;
  os_type?: string;
  os_version?: string;
  status: 'online' | 'offline' | 'error';
  last_heartbeat?: string;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  policy_id?: string;
  configuration: Record<string, any>;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Threat {
  id: string;
  organization_id: string;
  agent_id: string;
  threat_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'false_positive';
  title: string;
  description?: string;
  mitre_techniques: string[];
  source_ip?: string;
  destination_ip?: string;
  process_name?: string;
  file_path?: string;
  command_line?: string;
  user_account?: string;
  threat_score?: number;
  indicators: Record<string, any>;
  metadata: Record<string, any>;
  first_seen: string;
  last_seen: string;
  created_at: string;
  updated_at: string;
}

export interface Investigation {
  id: string;
  organization_id: string;
  threat_id?: string;
  title: string;
  description?: string;
  status: 'open' | 'in_progress' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: string;
  created_by: string;
  timeline: Array<{
    timestamp: string;
    action: string;
    user: string;
    details: string;
  }>;
  evidence: Array<{
    id: string;
    type: string;
    name: string;
    description?: string;
    file_url?: string;
    metadata: Record<string, any>;
    added_by: string;
    added_at: string;
  }>;
  notes?: string;
  findings?: string;
  conclusion?: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentResponse {
  id: string;
  organization_id: string;
  threat_id?: string;
  investigation_id?: string;
  response_type: string;
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  actions: Array<{
    id: string;
    type: string;
    target?: string;
    parameters: Record<string, any>;
    status: string;
    message?: string;
    executed_at?: string;
  }>;
  automated: boolean;
  approval_status: 'pending' | 'approved' | 'rejected';
  approved_by?: string;
  executed_at?: string;
  created_by: string;
  effectiveness_score?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  policy_type: string;
  configuration: Record<string, any>;
  is_active: boolean;
  version: number;
  deployed_agents: number;
  total_agents: number;
  created_by: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
}