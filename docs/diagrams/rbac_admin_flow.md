# WatchLockAI Sentinel RBAC & Admin Flow

This diagram illustrates the Role-Based Access Control (RBAC) system and administrative workflows within WatchLockAI Sentinel.

```mermaid
graph TD
    %% Entry Points
    A[User Request] --> B{Authentication Required?}
    A1[Admin Console] --> B
    A2[API Client] --> B
    A3[System Tray] --> B

    %% Authentication Flow
    B -->|Yes| C[Authentication Check]
    B -->|No| D[Public Access]
    
    C --> E{Valid Credentials?}
    E -->|No| F[401 Unauthorized]
    E -->|Yes| G[Session Creation]
    
    %% Session Management
    G --> H[RBAC Authorization]
    H --> I{Role Check}
    
    %% Role-Based Access Control
    I --> J[Admin Role]
    I --> K[User Role]
    I --> L[Guest Role]
    
    %% Admin Privileges
    J --> M[Full System Access]
    M --> N[Configuration Management]
    M --> O[User Management]
    M --> P[System Control]
    M --> Q[Data Export]
    M --> R[Security Settings]
    
    %% User Privileges
    K --> S[Limited Access]
    S --> T[View Metrics]
    S --> U[Health Status]
    S --> V[Basic Reports]
    
    %% Guest Privileges
    L --> W[Read-Only Access]
    W --> X[Public Metrics]
    W --> Y[System Status]
    
    %% Admin Operations
    N --> Z1[Feature Flags]
    N --> Z2[Rate Limits]
    N --> Z3[Logging Config]
    
    O --> Z4[Add Users]
    O --> Z5[Modify Roles]
    O --> Z6[Revoke Access]
    
    P --> Z7[Start/Stop Services]
    P --> Z8[Maintenance Mode]
    P --> Z9[Backup/Restore]
    
    Q --> Z10[CSV Export]
    Q --> Z11[JSON Export]
    Q --> Z12[Archive Data]
    
    R --> Z13[TLS Settings]
    R --> Z14[API Keys]
    R --> Z15[Audit Logs]
    
    %% Security Gating
    AA[Environment Flags] --> BB{RBAC_ENABLED?}
    BB -->|Yes| H
    BB -->|No| CC[Bypass RBAC]
    
    DD[ADMIN_TOKEN] --> EE{Token Valid?}
    EE -->|Yes| J
    EE -->|No| F
    
    %% Session Security
    G --> FF[Session Cookie]
    FF --> GG[HttpOnly + Secure]
    FF --> HH[SameSite Protection]
    FF --> II[Expiration Control]
    
    %% Request Flow
    M --> JJ[Action Validation]
    S --> JJ
    W --> JJ
    D --> JJ
    
    JJ --> KK{Authorized Action?}
    KK -->|Yes| LL[Execute Request]
    KK -->|No| MM[403 Forbidden]
    
    %% Audit Trail
    LL --> NN[Audit Logging]
    MM --> NN
    F --> NN
    
    NN --> OO[Security Events]
    NN --> PP[Access Logs]
    NN --> QQ[Admin Actions]
    
    %% Styling
    classDef auth fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef rbac fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef admin fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef security fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef audit fill:#e1f5fe,stroke:#0277bd,stroke-width:2px

    class A,A1,A2,A3,B,C,E,F,G auth
    class H,I,J,K,L,BB,CC rbac
    class M,N,O,P,Q,R,Z1,Z2,Z3,Z4,Z5,Z6,Z7,Z8,Z9,Z10,Z11,Z12,Z13,Z14,Z15 admin
    class AA,DD,EE,FF,GG,HH,II,JJ,KK,LL,MM security
    class NN,OO,PP,QQ audit
```

## Authentication Mechanisms

### Session-Based Authentication
- **Cookie Management**: HttpOnly, Secure, SameSite attributes
- **Session Expiration**: Configurable timeout and renewal
- **Token Validation**: HMAC-based session integrity

### API Token Authentication
- **Admin Token**: `ADMIN_TOKEN` environment variable
- **API Keys**: Per-client authentication tokens
- **Token Rotation**: Automated credential refresh

## Role Hierarchy

### Admin Role
**Full system privileges including:**
- Configuration management (feature flags, rate limits, logging)
- User and role management
- System control (start/stop services, maintenance mode)
- Data export and archival operations
- Security settings and TLS configuration

### User Role
**Limited operational access:**
- View system metrics and health status
- Generate basic reports
- Monitor system performance
- Access non-sensitive endpoints

### Guest Role
**Read-only public access:**
- Public metrics and system status
- Basic health information
- No configuration or control capabilities

## Security Controls

### Environment Flag Gating
- **RBAC_ENABLED**: Master switch for role-based access control
- **ADMIN_REQUIRE_AUTH**: Enforce authentication for admin endpoints
- **SESSION_REQUIRE_TLS**: Mandate TLS for session cookies

### Request Validation
1. **Authentication Check**: Verify session or token validity
2. **Role Authorization**: Confirm user has required role
3. **Action Validation**: Ensure specific operation is permitted
4. **Resource Access**: Validate access to requested resources

### Session Security
- **Secure Cookies**: Prevent client-side access and tampering
- **Cross-Site Protection**: SameSite attribute prevents CSRF
- **Session Fixation**: New session ID on authentication
- **Concurrent Sessions**: Optional session limit per user

## Admin Workflow Examples

### Configuration Change
1. Admin authenticates with valid credentials
2. RBAC confirms admin role assignment
3. Configuration endpoint validates permissions
4. Change applied with audit logging
5. System components notified of updates

### User Management
1. Admin accesses user management interface
2. Role verification confirms admin privileges
3. User creation/modification with validation
4. Role assignment with permission mapping
5. Audit trail records administrative action

### Data Export
1. Export request with admin authentication
2. EXPORT_ENABLED flag verification
3. Data access authorization check
4. Export generation with integrity hashing
5. Secure download with audit logging

## Audit and Compliance

### Security Event Logging
- Authentication attempts (success/failure)
- Authorization decisions and role checks
- Administrative actions and configuration changes
- Data access and export operations

### Access Control Monitoring
- Failed authentication attempts
- Privilege escalation attempts
- Unauthorized access attempts
- Session anomalies and security violations

### Compliance Features
- Complete audit trail for all administrative actions
- Role-based segregation of duties
- Configurable session and authentication policies
- Security event correlation and alerting
