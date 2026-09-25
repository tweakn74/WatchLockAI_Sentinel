CREATE TABLE incident_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    threat_id UUID,
    investigation_id UUID,
    response_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    actions JSONB DEFAULT '[]',
    automated BOOLEAN DEFAULT false,
    approval_status VARCHAR(50) DEFAULT 'pending',
    approved_by UUID,
    executed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL,
    effectiveness_score INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);