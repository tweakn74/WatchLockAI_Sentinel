import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

interface SeedRequest {
  action: 'seed_all' | 'seed_organization' | 'seed_threats' | 'seed_agents' | 'clear_data'
  organization_id?: string
}

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
    'Access-Control-Max-Age': '86400',
    'Access-Control-Allow-Credentials': 'false'
  }

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders })
  }

  try {
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!supabaseServiceKey) {
      throw new Error('Service role key not found')
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      supabaseServiceKey
    )

    const requestData: SeedRequest = await req.json()
    const { action, organization_id } = requestData

    let result: any = {}

    switch (action) {
      case 'seed_all':
        result = await seedAllData(supabase)
        break
      case 'seed_organization':
        result = await seedOrganization(supabase)
        break
      case 'seed_threats':
        const { data: existingAgents } = await supabase.from('agents').select('*').eq('organization_id', organization_id)
        result = await seedThreats(supabase, organization_id, existingAgents || [])
        break
      case 'seed_agents':
        result = await seedAgents(supabase, organization_id)
        break
      case 'clear_data':
        result = await clearAllData(supabase)
        break
      default:
        throw new Error('Invalid action specified')
    }

    return new Response(JSON.stringify({ data: result }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Seed database error:', error)
    
    const errorResponse = {
      error: {
        code: 'SEED_ERROR',
        message: error.message
      }
    }

    return new Response(JSON.stringify(errorResponse), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})

async function seedAllData(supabase: any) {
  console.log('Starting full database seeding...')
  
  // Seed organization first and get the generated ID
  const orgResult = await seedOrganization(supabase)
  const orgId = orgResult.organization.id
  console.log('Created organization with ID:', orgId)
  
  // Seed agents
  const agentsResult = await seedAgents(supabase, orgId)
  const agents = agentsResult.agents
  
  // Seed threats
  await seedThreats(supabase, orgId, agents)
  
  console.log('Database seeding completed successfully!')
  return { message: 'Database seeded successfully', organization_id: orgId }
}

async function seedOrganization(supabase: any) {
  const orgData = {
    name: 'Acme Corporation',
    subdomain: 'acme-corp',
    logo_url: null,
    settings: {
      timezone: 'UTC',
      retention_days: 90,
      alert_threshold: 'medium',
      domain: 'acme.com',
      plan_type: 'enterprise'
    }
  }

  const { data, error } = await supabase
    .from('organizations')
    .insert(orgData)
    .select()
    .single()

  if (error) throw error
  return { organization: data }
}

async function seedAgents(supabase: any, orgId: string) {
  const agents = [
    {
      organization_id: orgId,
      hostname: 'DESKTOP-ABC123',
      ip_address: '192.168.1.105',
      os_type: 'Windows 11',
      os_version: '22H2',
      status: 'online',
      agent_version: '1.2.3',
      last_heartbeat: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      cpu_usage: 23,
      memory_usage: 45,
      disk_usage: 67,
      configuration: {
        location: 'Office - Floor 2',
        user_account: 'jdoe'
      },
      tags: ['workstation', 'windows']
    },
    {
      organization_id: orgId,
      hostname: 'SRV-FILESERVER01',
      ip_address: '192.168.1.50',
      os_type: 'Windows Server 2022',
      os_version: '21H2',
      status: 'online',
      agent_version: '1.2.3',
      last_heartbeat: new Date(Date.now() - 1 * 60 * 1000).toISOString(),
      cpu_usage: 8,
      memory_usage: 62,
      disk_usage: 78,
      configuration: {
        location: 'Data Center - Rack 3',
        user_account: 'SYSTEM'
      },
      tags: ['server', 'windows', 'fileserver']
    },
    {
      organization_id: orgId,
      hostname: 'UBUNTU-WS-001',
      ip_address: '192.168.1.125',
      os_type: 'Ubuntu',
      os_version: '22.04.3 LTS',
      status: 'offline',
      agent_version: '1.2.2',
      last_heartbeat: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      cpu_usage: null,
      memory_usage: null,
      disk_usage: null,
      configuration: {
        location: 'Dev Lab - Station 4',
        user_account: 'developer'
      },
      tags: ['workstation', 'linux', 'development']
    }
  ]

  const { data, error } = await supabase
    .from('agents')
    .insert(agents)
    .select()

  if (error) throw error
  return { agents_created: agents.length, agents: data }
}

async function seedThreats(supabase: any, orgId: string, agents: any[]) {
  if (!agents || agents.length === 0) {
    return { threats_created: 0 }
  }

  const threats = [
    {
      organization_id: orgId,
      agent_id: agents[0].id,
      title: 'Suspicious PowerShell Execution',
      description: 'PowerShell script detected attempting to download and execute malicious payload from external domain',
      severity: 'critical',
      status: 'open',
      threat_type: 'Malware',
      threat_score: 95,
      first_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - 105 * 60 * 1000).toISOString(),
      source_ip: '192.168.1.105',
      destination_ip: '185.234.72.19',
      process_name: 'powershell.exe',
      file_path: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
      user_account: 'DESKTOP-ABC123\\jdoe',
      command_line: 'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden',
      mitre_techniques: ['T1059.001', 'T1105', 'T1140'],
      indicators: ['malicious-domain.com', 'payload.ps1', 'ExecutionPolicy Bypass'],
      metadata: {
        confidence: 0.95,
        alert_id: 'ALT-2025-001'
      }
    },
    {
      organization_id: orgId,
      agent_id: agents[1].id,
      title: 'Ransomware File Encryption Activity',
      description: 'Rapid file modification pattern detected consistent with ransomware encryption behavior',
      severity: 'critical',
      status: 'investigating',
      threat_type: 'Ransomware',
      threat_score: 98,
      first_seen: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - 135 * 60 * 1000).toISOString(),
      source_ip: '192.168.1.50',
      destination_ip: null,
      process_name: 'encrypt_files.exe',
      file_path: 'C:\\Temp\\encrypt_files.exe',
      user_account: 'NT AUTHORITY\\SYSTEM',
      command_line: 'encrypt_files.exe --target C:\\Users --extension .locked',
      mitre_techniques: ['T1486', 'T1027', 'T1083'],
      indicators: ['encrypt_files.exe', '.locked', 'rapid_file_changes'],
      metadata: {
        confidence: 0.98,
        alert_id: 'ALT-2025-002',
        files_affected: 1247
      }
    }
  ]

  const { data, error } = await supabase
    .from('threats')
    .insert(threats)
    .select()

  if (error) throw error
  return { threats_created: threats.length, threats: data }
}

async function clearAllData(supabase: any) {
  console.log('Clearing all data...')
  
  const tables = [
    'audit_logs',
    'reports', 
    'integrations',
    'policies',
    'incident_responses',
    'investigations',
    'threats',
    'agents',
    'user_profiles',
    'organizations'
  ]

  for (const table of tables) {
    const { error } = await supabase
      .from(table)
      .delete()
      .neq('id', 'never_match')
      
    if (error) {
      console.error(`Error clearing ${table}:`, error)
    }
  }
  
  return { message: 'All data cleared successfully' }
}