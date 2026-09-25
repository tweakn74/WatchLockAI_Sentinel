Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, agent_data } = await req.json();
        
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        
        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        if (action === 'heartbeat') {
            // Agent sending health status
            const updateResponse = await fetch(`${supabaseUrl}/rest/v1/agents?id=eq.${agent_data.agent_id}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    status: 'online',
                    last_heartbeat: new Date().toISOString(),
                    cpu_usage: agent_data.cpu_usage,
                    memory_usage: agent_data.memory_usage,
                    disk_usage: agent_data.disk_usage,
                    agent_version: agent_data.agent_version,
                    updated_at: new Date().toISOString()
                })
            });

            if (!updateResponse.ok) {
                const errorText = await updateResponse.text();
                throw new Error(`Failed to update agent: ${errorText}`);
            }

            const agentData = await updateResponse.json();
            
            return new Response(JSON.stringify({
                data: { agent: agentData[0] || {}, status: 'updated' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'register_agent') {
            // New agent registration
            const createResponse = await fetch(`${supabaseUrl}/rest/v1/agents`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    organization_id: agent_data.organization_id,
                    hostname: agent_data.hostname,
                    ip_address: agent_data.ip_address,
                    agent_version: agent_data.agent_version,
                    os_type: agent_data.os_type,
                    os_version: agent_data.os_version,
                    status: 'online',
                    last_heartbeat: new Date().toISOString(),
                    configuration: agent_data.configuration || {},
                    tags: agent_data.tags || []
                })
            });

            if (!createResponse.ok) {
                const errorText = await createResponse.text();
                throw new Error(`Failed to register agent: ${errorText}`);
            }

            const newAgent = await createResponse.json();
            
            // Create audit log
            await fetch(`${supabaseUrl}/rest/v1/audit_logs`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    organization_id: agent_data.organization_id,
                    action: 'agent_registered',
                    resource_type: 'agent',
                    resource_id: newAgent[0].id,
                    details: {
                        hostname: agent_data.hostname,
                        os_type: agent_data.os_type
                    }
                })
            });
            
            return new Response(JSON.stringify({
                data: { agent: newAgent[0], status: 'registered' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'get_agents') {
            // Get agents for dashboard
            const orgId = agent_data.organization_id;
            const status = agent_data.status || null;
            
            let url = `${supabaseUrl}/rest/v1/agents?organization_id=eq.${orgId}&order=updated_at.desc`;
            if (status) {
                url += `&status=eq.${status}`;
            }
            
            const agentsResponse = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            if (!agentsResponse.ok) {
                throw new Error('Failed to fetch agents');
            }

            const agents = await agentsResponse.json();
            
            // Calculate health metrics
            const totalAgents = agents.length;
            const onlineAgents = agents.filter(a => a.status === 'online').length;
            const offlineAgents = agents.filter(a => a.status === 'offline').length;
            const unhealthyAgents = agents.filter(a => 
                a.cpu_usage > 80 || a.memory_usage > 85 || a.disk_usage > 90
            ).length;
            
            return new Response(JSON.stringify({
                data: {
                    agents,
                    metrics: {
                        total: totalAgents,
                        online: onlineAgents,
                        offline: offlineAgents,
                        unhealthy: unhealthyAgents
                    }
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action specified');

    } catch (error) {
        console.error('Agent health error:', error);
        
        const errorResponse = {
            error: {
                code: 'AGENT_HEALTH_ERROR',
                message: error.message
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});