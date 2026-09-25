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
        const { action, threat_data } = await req.json();
        
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        
        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        if (action === 'report_threat') {
            // Agent reporting a new threat
            const threatResponse = await fetch(`${supabaseUrl}/rest/v1/threats`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    organization_id: threat_data.organization_id,
                    agent_id: threat_data.agent_id,
                    threat_type: threat_data.threat_type,
                    severity: threat_data.severity,
                    title: threat_data.title,
                    description: threat_data.description,
                    mitre_techniques: threat_data.mitre_techniques || [],
                    source_ip: threat_data.source_ip,
                    destination_ip: threat_data.destination_ip,
                    process_name: threat_data.process_name,
                    file_path: threat_data.file_path,
                    command_line: threat_data.command_line,
                    user_account: threat_data.user_account,
                    threat_score: threat_data.threat_score,
                    indicators: threat_data.indicators || {},
                    metadata: threat_data.metadata || {}
                })
            });

            if (!threatResponse.ok) {
                const errorText = await threatResponse.text();
                throw new Error(`Failed to create threat: ${errorText}`);
            }

            const threatData = await threatResponse.json();
            
            // Create audit log
            await fetch(`${supabaseUrl}/rest/v1/audit_logs`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    organization_id: threat_data.organization_id,
                    action: 'threat_detected',
                    resource_type: 'threat',
                    resource_id: threatData[0].id,
                    details: {
                        agent_id: threat_data.agent_id,
                        threat_type: threat_data.threat_type,
                        severity: threat_data.severity
                    }
                })
            });

            return new Response(JSON.stringify({
                data: { threat: threatData[0], status: 'created' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'get_threats') {
            // Get threats for dashboard
            const orgId = threat_data.organization_id;
            const limit = threat_data.limit || 50;
            const status = threat_data.status || 'open';
            
            const threatsResponse = await fetch(`${supabaseUrl}/rest/v1/threats?organization_id=eq.${orgId}&status=eq.${status}&order=created_at.desc&limit=${limit}`, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            if (!threatsResponse.ok) {
                throw new Error('Failed to fetch threats');
            }

            const threats = await threatsResponse.json();
            
            return new Response(JSON.stringify({
                data: { threats, count: threats.length }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action specified');

    } catch (error) {
        console.error('Threat monitoring error:', error);
        
        const errorResponse = {
            error: {
                code: 'THREAT_MONITOR_ERROR',
                message: error.message
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});