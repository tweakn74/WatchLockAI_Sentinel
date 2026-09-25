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
        const { action, response_data, user_id } = await req.json();
        
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        
        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        if (action === 'create_response') {
            // Create incident response
            const createResponse = await fetch(`${supabaseUrl}/rest/v1/incident_responses`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    organization_id: response_data.organization_id,
                    threat_id: response_data.threat_id,
                    investigation_id: response_data.investigation_id,
                    response_type: response_data.response_type,
                    priority: response_data.priority || 'medium',
                    automated: response_data.automated || false,
                    actions: response_data.actions || [],
                    created_by: user_id,
                    notes: response_data.notes
                })
            });

            if (!createResponse.ok) {
                const errorText = await createResponse.text();
                throw new Error(`Failed to create response: ${errorText}`);
            }

            const responseData = await createResponse.json();
            
            // Create audit log
            await fetch(`${supabaseUrl}/rest/v1/audit_logs`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    organization_id: response_data.organization_id,
                    user_id: user_id,
                    action: 'incident_response_created',
                    resource_type: 'incident_response',
                    resource_id: responseData[0].id,
                    details: {
                        response_type: response_data.response_type,
                        threat_id: response_data.threat_id
                    }
                })
            });
            
            return new Response(JSON.stringify({
                data: { response: responseData[0], status: 'created' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'execute_response') {
            // Execute incident response actions
            const responseId = response_data.response_id;
            const actions = response_data.actions;
            
            // Simulate response execution (in real implementation, this would integrate with endpoint agents)
            const executionResults = [];
            
            for (const action of actions) {
                let result = {
                    action_id: action.id,
                    action_type: action.type,
                    status: 'success',
                    message: 'Action executed successfully',
                    executed_at: new Date().toISOString()
                };
                
                // Simulate different action types
                switch (action.type) {
                    case 'isolate_endpoint':
                        result.message = `Endpoint ${action.target} isolated successfully`;
                        break;
                    case 'kill_process':
                        result.message = `Process ${action.process_name} terminated on ${action.target}`;
                        break;
                    case 'block_ip':
                        result.message = `IP ${action.ip_address} blocked in firewall`;
                        break;
                    case 'quarantine_file':
                        result.message = `File ${action.file_path} quarantined successfully`;
                        break;
                    case 'reset_password':
                        result.message = `Password reset for user ${action.username}`;
                        break;
                    default:
                        result.message = `Custom action ${action.type} executed`;
                }
                
                executionResults.push(result);
            }
            
            // Update response record
            const updateResponse = await fetch(`${supabaseUrl}/rest/v1/incident_responses?id=eq.${responseId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    status: 'completed',
                    executed_at: new Date().toISOString(),
                    actions: executionResults,
                    effectiveness_score: response_data.effectiveness_score || 85
                })
            });
            
            if (!updateResponse.ok) {
                throw new Error('Failed to update response status');
            }
            
            const updatedResponse = await updateResponse.json();
            
            return new Response(JSON.stringify({
                data: { 
                    response: updatedResponse[0], 
                    execution_results: executionResults,
                    status: 'executed' 
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'approve_response') {
            // Approve pending response
            const responseId = response_data.response_id;
            
            const updateResponse = await fetch(`${supabaseUrl}/rest/v1/incident_responses?id=eq.${responseId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    approval_status: 'approved',
                    approved_by: user_id,
                    status: 'approved'
                })
            });
            
            if (!updateResponse.ok) {
                throw new Error('Failed to approve response');
            }
            
            const approvedResponse = await updateResponse.json();
            
            return new Response(JSON.stringify({
                data: { response: approvedResponse[0], status: 'approved' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'get_responses') {
            // Get incident responses
            const orgId = response_data.organization_id;
            const status = response_data.status;
            const threatId = response_data.threat_id;
            
            let url = `${supabaseUrl}/rest/v1/incident_responses?organization_id=eq.${orgId}&order=created_at.desc`;
            if (status) url += `&status=eq.${status}`;
            if (threatId) url += `&threat_id=eq.${threatId}`;
            
            const responsesResponse = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            if (!responsesResponse.ok) {
                throw new Error('Failed to fetch responses');
            }

            const responses = await responsesResponse.json();
            
            return new Response(JSON.stringify({
                data: { responses, count: responses.length }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action specified');

    } catch (error) {
        console.error('Response automation error:', error);
        
        const errorResponse = {
            error: {
                code: 'RESPONSE_AUTOMATION_ERROR',
                message: error.message
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});