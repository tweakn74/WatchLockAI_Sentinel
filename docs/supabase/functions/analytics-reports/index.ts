// Helper functions
function calculateThreatTrends(threats) {
    const trends = {};
    threats.forEach(threat => {
        const date = new Date(threat.created_at).toDateString();
        trends[date] = (trends[date] || 0) + 1;
    });
    return trends;
}

function calculateMitreBreakdown(threats) {
    const mitreCount = {};
    threats.forEach(threat => {
        if (threat.mitre_techniques) {
            threat.mitre_techniques.forEach(technique => {
                mitreCount[technique] = (mitreCount[technique] || 0) + 1;
            });
        }
    });
    return mitreCount;
}

function calculateAverageResponseTime(responses) {
    if (responses.length === 0) return 0;
    
    const responseTimes = responses
        .filter(r => r.response_time_minutes)
        .map(r => r.response_time_minutes);
        
    if (responseTimes.length === 0) return 0;
    return responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
}

function calculateDetectionRate(threats, agents) {
    const activeAgents = agents.filter(a => a.status === 'online').length;
    if (activeAgents === 0) return 0;
    return Math.min(100, (threats.length / activeAgents) * 10);
}

function calculateRiskScore(threats, agents) {
    const criticalThreats = threats.filter(t => t.severity === 'critical').length;
    const totalAgents = agents.length;
    const offlineAgents = agents.filter(a => a.status === 'offline').length;
    
    if (totalAgents === 0) return 0;
    return Math.min(100, (criticalThreats * 20) + (offlineAgents / totalAgents * 30));
}

function generateKeyFindings(threats, investigations) {
    return [
        `${threats.length} security threats detected in the reporting period`,
        `${threats.filter(t => t.severity === 'critical').length} critical incidents requiring immediate attention`,
        `${investigations.filter(i => i.status === 'open').length} ongoing investigations`
    ];
}

function generateRecommendations(threats, agents) {
    const recommendations = [];
    
    if (threats.filter(t => t.severity === 'critical').length > 0) {
        recommendations.push('Prioritize response to critical security threats');
    }
    
    if (agents.filter(a => a.status === 'offline').length > 0) {
        recommendations.push('Investigate and remediate offline security agents');
    }
    
    return recommendations;
}

function analyzeThreatPatterns(threats) {
    return {
        common_types: threats.reduce((acc, t) => {
            acc[t.threat_type] = (acc[t.threat_type] || 0) + 1;
            return acc;
        }, {}),
        severity_distribution: threats.reduce((acc, t) => {
            acc[t.severity] = (acc[t.severity] || 0) + 1;
            return acc;
        }, {})
    };
}

function analyzeMitreTechniques(threats) {
    const techniques = {};
    threats.forEach(threat => {
        if (threat.mitre_techniques) {
            threat.mitre_techniques.forEach(technique => {
                techniques[technique] = (techniques[technique] || 0) + 1;
            });
        }
    });
    return techniques;
}

function analyzeAgentPerformance(agents) {
    return {
        total: agents.length,
        online: agents.filter(a => a.status === 'online').length,
        performance_issues: agents.filter(a => a.cpu_usage > 80 || a.memory_usage > 85).length,
        avg_cpu: agents.reduce((sum, a) => sum + (a.cpu_usage || 0), 0) / agents.length,
        avg_memory: agents.reduce((sum, a) => sum + (a.memory_usage || 0), 0) / agents.length
    };
}

function analyzeInvestigations(investigations) {
    return {
        total: investigations.length,
        by_status: investigations.reduce((acc, i) => {
            acc[i.status] = (acc[i.status] || 0) + 1;
            return acc;
        }, {}),
        by_priority: investigations.reduce((acc, i) => {
            acc[i.priority] = (acc[i.priority] || 0) + 1;
            return acc;
        }, {})
    };
}

function analyzeResponseEffectiveness(responses) {
    return {
        total: responses.length,
        avg_response_time: calculateAverageResponseTime(responses),
        success_rate: responses.filter(r => r.status === 'completed').length / responses.length * 100
    };
}

function generateChartData(threats, agents, investigations) {
    return {
        threat_trends: calculateThreatTrends(threats),
        agent_status: {
            online: agents.filter(a => a.status === 'online').length,
            offline: agents.filter(a => a.status === 'offline').length
        },
        investigation_status: {
            open: investigations.filter(i => i.status === 'open').length,
            closed: investigations.filter(i => i.status === 'closed').length
        }
    };
}

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
        const { action, report_data, user_id } = await req.json();
        
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        
        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        if (action === 'generate_dashboard_metrics') {
            const orgId = report_data.organization_id;
            const timeRange = report_data.time_range || '24h';
            
            // Calculate time filter based on range
            const now = new Date();
            let startTime = new Date();
            
            switch (timeRange) {
                case '1h':
                    startTime.setHours(now.getHours() - 1);
                    break;
                case '24h':
                    startTime.setDate(now.getDate() - 1);
                    break;
                case '7d':
                    startTime.setDate(now.getDate() - 7);
                    break;
                case '30d':
                    startTime.setDate(now.getDate() - 30);
                    break;
                default:
                    startTime.setDate(now.getDate() - 1);
            }
            
            const timeFilter = `&created_at=gte.${startTime.toISOString()}`;
            
            // Fetch threats data
            const threatsResponse = await fetch(`${supabaseUrl}/rest/v1/threats?organization_id=eq.${orgId}${timeFilter}`, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });
            
            const threats = await threatsResponse.json();
            
            // Fetch agents data
            const agentsResponse = await fetch(`${supabaseUrl}/rest/v1/agents?organization_id=eq.${orgId}`, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });
            
            const agents = await agentsResponse.json();
            
            // Calculate metrics
            const metrics = {
                threats: {
                    total: threats.length,
                    critical: threats.filter(t => t.severity === 'critical').length,
                    high: threats.filter(t => t.severity === 'high').length,
                    medium: threats.filter(t => t.severity === 'medium').length,
                    low: threats.filter(t => t.severity === 'low').length,
                    resolved: threats.filter(t => t.status === 'resolved').length,
                    open: threats.filter(t => t.status === 'open').length
                },
                agents: {
                    total: agents.length,
                    online: agents.filter(a => a.status === 'online').length,
                    offline: agents.filter(a => a.status === 'offline').length,
                    unhealthy: agents.filter(a => a.cpu_usage > 80 || a.memory_usage > 85).length
                },
                response_time: 4.2, // Static for demo
                detection_rate: calculateDetectionRate(threats, agents),
                risk_score: calculateRiskScore(threats, agents)
            };
            
            return new Response(JSON.stringify({
                data: { metrics, generated_at: new Date().toISOString() }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
        
        if (action === 'generate_security_report') {
            const orgId = report_data.organization_id;
            const reportType = report_data.report_type || 'security_summary';
            
            // For demo purposes, return basic report structure
            const reportData = {
                title: 'Security Summary Report',
                period: '30 days',
                overview: {
                    threats: 0,
                    agents: 0,
                    investigations: 0,
                    responses: 0
                }
            };
            
            return new Response(JSON.stringify({
                data: { report: reportData, status: 'generated' }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action specified');

    } catch (error) {
        console.error('Analytics reports error:', error);
        
        const errorResponse = {
            error: {
                code: 'ANALYTICS_ERROR',
                message: error.message
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});