CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    integration_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    configuration JSONB DEFAULT '{}',
    credentials JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'inactive',
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_frequency VARCHAR(50),
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);