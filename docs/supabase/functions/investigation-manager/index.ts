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
        const { action, investigation_data, user_id } = await req.json();
        
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        
        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        if (action === 'create_investigation') {
            // Create new investigation case
            const createResponse = await fetch(`${supabaseUrl}/rest/v1/investigations`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    organization_id: investigation_data.organization_id,
                    threat_id: investigation_data.threat_id,
                    title: investigation_data.title,
                    description: investigation_data.description,
                    priority: investigation_data.priority || 'medium',
                    assigned_to: investigation_data.assigned_to,
                    created_by: user_id,
                    timeline: [{
                        timestamp: new Date().toISOString(),
                        action: 'investigation_created',
                        user: user_id,
                        details: 'Investigation case opened'
                    }]
                })
            });

            if (!createResponse.ok) {
                const errorText = await createResponse.text();
                throw new Error(`Failed to create investigation: ${errorText}`);
            }

            const investigationData = await createResponse.json();
            
            // Create audit log
            await fetch(`${supabaseUrl}/rest/v1/audit_logs`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    organization_id: investigation_data.organization_id,
                    user_id: user_id,
                    action: 'investigation_created',
                    resource_type: 'investigation',
                    resource_id: investigationData[0].id,
                    details: {
                        threat_id: investigation_data.threat_id,
                        title: investigation_data.title
                    }
                })
            });
            
            return new Response(JSON.stringify({
                data: { investigation: investigationData[0], status: 'created' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'add_evidence') {
            // Add evidence to investigation
            const investigationId = investigation_data.investigation_id;
            const newEvidence = investigation_data.evidence;
            
            // Get current investigation
            const getResponse = await fetch(`${supabaseUrl}/rest/v1/investigations?id=eq.${investigationId}`, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });
            
            if (!getResponse.ok) {
                throw new Error('Investigation not found');
            }
            
            const investigations = await getResponse.json();
            if (investigations.length === 0) {
                throw new Error('Investigation not found');
            }
            
            const currentEvidence = investigations[0].evidence || [];
            const currentTimeline = investigations[0].timeline || [];
            
            // Update evidence and timeline
            const updateResponse = await fetch(`${supabaseUrl}/rest/v1/investigations?id=eq.${investigationId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    evidence: [...currentEvidence, {
                        id: crypto.randomUUID(),
                        type: newEvidence.type,
                        name: newEvidence.name,
                        description: newEvidence.description,
                        file_url: newEvidence.file_url,
                        metadata: newEvidence.metadata || {},
                        added_by: user_id,
                        added_at: new Date().toISOString()
                    }],
                    timeline: [...currentTimeline, {
                        timestamp: new Date().toISOString(),
                        action: 'evidence_added',
                        user: user_id,
                        details: `Added evidence: ${newEvidence.name}`
                    }],
                    updated_at: new Date().toISOString()
                })
            });
            
            if (!updateResponse.ok) {
                throw new Error('Failed to add evidence');
            }
            
            const updatedInvestigation = await updateResponse.json();
            
            return new Response(JSON.stringify({
                data: { investigation: updatedInvestigation[0], status: 'evidence_added' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'update_findings') {
            // Update investigation findings
            const investigationId = investigation_data.investigation_id;
            const findings = investigation_data.findings;
            const conclusion = investigation_data.conclusion;
            const status = investigation_data.status;
            
            // Get current timeline
            const getResponse = await fetch(`${supabaseUrl}/rest/v1/investigations?id=eq.${investigationId}`, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });
            
            const investigations = await getResponse.json();
            const currentTimeline = investigations[0]?.timeline || [];
            
            const updateResponse = await fetch(`${supabaseUrl}/rest/v1/investigations?id=eq.${investigationId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    findings: findings,
                    conclusion: conclusion,
                    status: status,
                    timeline: [...currentTimeline, {
                        timestamp: new Date().toISOString(),
                        action: 'findings_updated',
                        user: user_id,
                        details: status === 'closed' ? 'Investigation completed' : 'Findings updated'
                    }],
                    updated_at: new Date().toISOString()
                })
            });
            
            if (!updateResponse.ok) {
                throw new Error('Failed to update findings');
            }
            
            const updatedInvestigation = await updateResponse.json();
            
            return new Response(JSON.stringify({
                data: { investigation: updatedInvestigation[0], status: 'updated' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'get_investigations') {
            // Get investigations for organization
            const orgId = investigation_data.organization_id;
            const status = investigation_data.status;
            const assignedTo = investigation_data.assigned_to;
            
            let url = `${supabaseUrl}/rest/v1/investigations?organization_id=eq.${orgId}&order=created_at.desc`;
            if (status) url += `&status=eq.${status}`;
            if (assignedTo) url += `&assigned_to=eq.${assignedTo}`;
            
            const investigationsResponse = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            if (!investigationsResponse.ok) {
                throw new Error('Failed to fetch investigations');
            }

            const investigations = await investigationsResponse.json();
            
            return new Response(JSON.stringify({
                data: { investigations, count: investigations.length }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action specified');

    } catch (error) {
        console.error('Investigation manager error:', error);
        
        const errorResponse = {
            error: {
                code: 'INVESTIGATION_ERROR',
                message: error.message
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});