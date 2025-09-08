# WatchLockAI Sentinel - Operations Runbook (P5-006)

**Version:** 3.0 (P5 Release Candidate)  
**Last Updated:** 2025-09-06  
**Owner:** Operations Team  
**Scope:** Production deployment, maintenance, and incident response

## Table of Contents

1. [System Overview](#system-overview)
2. [Deployment Procedures](#deployment-procedures)
3. [Backup & Restore Operations](#backup--restore-operations)
4. [Secret Rotation Procedures](#secret-rotation-procedures)
5. [Chaos Testing & Resilience](#chaos-testing--resilience)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Incident Response](#incident-response)
8. [Maintenance Procedures](#maintenance-procedures)
9. [Data Retention & Cleanup](#data-retention--cleanup)
10. [Performance Testing & Monitoring](#performance-testing--monitoring)
11. [Offline Installation & Deployment](#offline-installation--deployment)
12. [Troubleshooting Guide](#troubleshooting-guide)
13. [Emergency Procedures](#emergency-procedures)
14. [RBAC Flow Diagram](#rbac-flow-diagram)

## System Overview

### Architecture Components

```
┌─────────────────────────┐
│       WatchLockAI Sentinel      │
│                               │
│  ┌──────────┐  ┌──────────┐  │
│  │ Collectors │  │ Rules Eng │  │
│  └──────────┘  └──────────┘  │
│                               │
│  ┌──────────┐  ┌──────────┐  │
│  │   Web API  │  │  Console  │  │
│  └──────────┘  └──────────┘  │
└─────────────────────────┘
```

### Key Features
- **Multi-Tenant Architecture:** Isolated data and configurations per tenant
- **MITRE ATT&CK Integration:** Advanced threat detection and classification
- **Real-Time Processing:** Event stream processing with configurable rules
- **Web-Based Management:** FastAPI-powered REST API and web console
- **Windows Service Support:** Native Windows deployment

### System Requirements
- **Operating System:** Windows 10/11, Windows Server 2019+
- **Python:** 3.8+ (3.10+ recommended)
- **Memory:** 4GB minimum, 8GB recommended
- **Disk Space:** 10GB minimum, 50GB recommended
- **Network:** Outbound HTTPS (443) for threat intelligence

## Deployment Procedures

### Initial Deployment

#### 1. Pre-Deployment Validation

```powershell
# Run preflight checks
cd C:\WatchLockAI_Sentinel
python console\preflight_checks.py --verbose

# Validate configuration
python tools\config_migrate.py --scan-environment --preview

# Security scan
python tools\sec_lint.py --fail-on-high
```

#### 2. Windows Service Installation

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Install service
.\scripts\install_service.ps1 -ServiceName "WatchLockAI_Sentinel" -DisplayName "WatchLockAI Sentinel Security Platform"

# Verify installation
Get-Service -Name "WatchLockAI_Sentinel"
```

#### 3. Configuration Setup

```powershell
# Copy template configuration
copy config.yaml.template config.yaml

# Edit configuration (use your preferred editor)
notepad config.yaml

# Validate configuration
python tools\config_migrate.py --validate-file config.yaml
```

#### 4. Service Startup

```powershell
# Start service
Start-Service -Name "WatchLockAI_Sentinel"

# Check status
Get-Service -Name "WatchLockAI_Sentinel" | Format-List

# Verify web interface
Start-Process "http://localhost:8080/api/metrics/health"
```

### Production Deployment Checklist

- [ ] **System Requirements:** Verified hardware and software requirements
- [ ] **Security Scan:** No HIGH severity security issues
- [ ] **Configuration:** All environment variables configured
- [ ] **Backup Setup:** Backup directory configured and accessible
- [ ] **Monitoring:** Health endpoints responding
- [ ] **Firewall:** Port 8080 configured (if remote access needed)
- [ ] **Logging:** Log directory writable, rotation configured
- [ ] **Service Account:** Appropriate permissions configured
- [ ] **SSL/TLS:** HTTPS configured for production (if applicable)
- [ ] **Documentation:** Runbook accessible to operations team

## Backup & Restore Operations

### Automated Backup

#### Enable Backup System

```powershell
# Enable backup functionality
$env:BACKUP_ENABLED = "1"
$env:BACKUP_DIR = "C:\WatchLockAI_Sentinel\backups"

# Create backup directory
New-Item -ItemType Directory -Force -Path $env:BACKUP_DIR
```

#### Create Manual Backup

```python
# Via Python API
python -c "
from console.backup_restore import get_backup_manager
bm = get_backup_manager()
result = bm.create_backup('Pre-maintenance backup')
print(f'Backup created: {result}')
"
```

#### Via REST API

```powershell
# Create backup via API (requires admin auth)
$headers = @{ "X-Admin-Token" = "your-admin-token" }
Invoke-RestMethod -Uri "http://localhost:8080/api/admin/backup" -Method POST -Headers $headers
```

### Restore Operations

#### Restore from Backup

```python
# Dry run first
python -c "
from console.backup_restore import get_backup_manager
bm = get_backup_manager()
result = bm.restore_backup('backups/sentinel_backup_20250905_120000.zip', confirm=False)
print(f'Restore plan: {result}')
"

# Actual restore
python -c "
from console.backup_restore import get_backup_manager
bm = get_backup_manager()
result = bm.restore_backup('backups/sentinel_backup_20250905_120000.zip', confirm=True)
print(f'Restore result: {result}')
"
```

#### Emergency Restore Procedure

1. **Stop Service**
   ```powershell
   Stop-Service -Name "WatchLockAI_Sentinel"
   ```

2. **Backup Current State** (if possible)
   ```powershell
   Copy-Item -Recurse data data_emergency_backup
   ```

3. **Restore from Backup**
   ```python
   # Use restore commands above
   ```

4. **Validate Configuration**
   ```powershell
   python tools\config_migrate.py --validate-file config.yaml
   ```

5. **Start Service**
   ```powershell
   Start-Service -Name "WatchLockAI_Sentinel"
   ```

### Backup Schedule Recommendations

- **Daily:** Automated configuration and state backup
- **Weekly:** Full system backup including logs
- **Pre-Change:** Manual backup before any configuration changes
- **Retention:** Keep 30 days of daily backups, 12 weeks of weekly backups

## Secret Rotation Procedures

### Scheduled Rotation

#### Monthly Secret Rotation

```powershell
# Enable secret rotation
$env:ROTATE_ENABLED = "1"

# Preview rotation plan
python tools\rotate_secrets.py --action preview --verbose

# Execute rotation
python tools\rotate_secrets.py --action execute --verbose

# Update environment variables with new secrets
# (Update your environment configuration with the new values)
```

#### Emergency Rotation

```powershell
# In case of suspected compromise
# 1. Immediately rotate all secrets
python tools\rotate_secrets.py --action execute --secrets ADMIN_TOKEN CONSOLE_AUTH_SESSION_KEY

# 2. Update running service
Restart-Service -Name "WatchLockAI_Sentinel"

# 3. Verify new secrets work
curl -H "X-Admin-Token: NEW_TOKEN" http://localhost:8080/api/admin/config/reload
```

### API Key Management

#### Admin Token Rotation

```python
# Generate new admin token
python -c "
from tools.rotate_secrets import get_secret_rotator
sr = get_secret_rotator()
result = sr.rotate_admin_token()
print(f'New admin token: {result}')
"
```

#### Session Key Rotation

```python
# Generate new session key
python -c "
from tools.rotate_secrets import get_secret_rotator
sr = get_secret_rotator()
result = sr.rotate_console_auth_session_key()
print(f'New session key: {result}')
"
```

### Post-Rotation Validation

```powershell
# Test admin API access
curl -H "X-Admin-Token: NEW_TOKEN" http://localhost:8080/api/admin/config/reload

# Test console authentication (if enabled)
# Access web console and verify login works

# Run self-check
python tools\self_check.py --verbose
```

## Chaos Testing & Resilience

### Chaos Engineering Setup

```powershell
# Enable chaos testing
$env:CHAOS_ENABLED = "1"
$env:CHAOS_MAX_LATENCY_MS = "2000"
$env:CHAOS_ERROR_RATE = "0.05"  # 5% error rate
```

### Scheduled Resilience Testing

#### Weekly Chaos Tests

```python
# Test latency injection
python -c "
from console.chaos_probes import get_chaos_manager
cm = get_chaos_manager()
result = cm.inject_latency('event_bus', 1000)
print(f'Latency injection: {result}')
"

# Test error injection
python -c "
from console.chaos_probes import get_chaos_manager
cm = get_chaos_manager()
result = cm.inject_error('rules_engine', 'exception', 0.1)
print(f'Error injection: {result}')
"
```

#### Production Resilience Validation

```powershell
# Test service recovery
Stop-Service -Name "WatchLockAI_Sentinel"
Start-Sleep -Seconds 5
Start-Service -Name "WatchLockAI_Sentinel"

# Verify health after restart
curl http://localhost:8080/api/metrics/health

# Test API rate limiting
# (Use load testing tool to verify rate limits work)
```

### Chaos Test Scenarios

1. **Network Latency:** Inject 500-2000ms latency
2. **Service Exceptions:** Random exceptions in core components
3. **Resource Exhaustion:** High CPU/memory usage simulation
4. **Configuration Corruption:** Invalid configuration scenarios
5. **Disk Full:** Simulate disk space exhaustion

## Monitoring & Health Checks

### Health Endpoint Monitoring

```powershell
# Basic health check
curl http://localhost:8080/api/metrics/health

# Detailed system status
curl http://localhost:8080/api/status

# Event bus metrics (if debug enabled)
curl http://localhost:8080/api/metrics/event_bus
```

### Automated Health Monitoring

```powershell
# Windows scheduled task for health monitoring
schtasks /create /tn "Sentinel Health Check" /tr "python C:\WatchLockAI_Sentinel\tools\self_check.py" /sc HOURLY
```

### Key Metrics to Monitor

#### System Health
- **Service Status:** Windows service running state
- **API Responsiveness:** Health endpoint response time < 5s
- **Memory Usage:** < 80% of available RAM
- **Disk Space:** > 20% free space in data directory
- **CPU Usage:** Average < 70% over 5 minutes

#### Application Metrics
- **Event Processing Rate:** Events processed per minute
- **Rule Engine Performance:** Rule evaluation time
- **Alert Generation:** Alert count and false positive rate
- **Error Rates:** HTTP 5xx responses < 1%
- **Authentication:** Failed authentication attempts

#### Security Metrics
- **Threat Detection:** MITRE ATT&CK rule triggers
- **Quarantine Actions:** Files quarantined per day
- **Access Attempts:** Admin API access patterns
- **Configuration Changes:** Unauthorized configuration modifications

### Alerting Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Service Down | - | Immediate | Restart service, escalate |
| API Response Time | > 5s | > 30s | Check resources, restart |
| Memory Usage | > 80% | > 95% | Restart service |
| Disk Space | < 20% | < 10% | Clean logs, add storage |
| Error Rate | > 1% | > 5% | Check logs, investigate |
| Failed Auth | > 10/hour | > 50/hour | Security review |

## Incident Response

### Severity Classification

#### Severity 1 (Critical)
- Service completely down
- Security breach detected
- Data corruption or loss
- Complete loss of monitoring

#### Severity 2 (High)
- Degraded performance affecting users
- Authentication system failure
- Backup system failure
- High error rates (> 5%)

#### Severity 3 (Medium)
- Non-critical feature failures
- Performance degradation
- Configuration issues
- Monitoring alerts

#### Severity 4 (Low)
- Cosmetic issues
- Documentation problems
- Enhancement requests

### Incident Response Procedures

#### Immediate Response (First 15 minutes)

1. **Assess Severity**
   ```powershell
   # Check service status
   Get-Service -Name "WatchLockAI_Sentinel"
   
   # Quick health check
   python tools\self_check.py
   
   # Check recent logs
   Get-Content logs\sentinel.log -Tail 50
   ```

2. **Containment Actions**
   - If security incident: Isolate affected systems
   - If service failure: Attempt service restart
   - If data corruption: Stop writes, preserve state

3. **Communication**
   - Notify incident response team
   - Document initial findings
   - Establish communication channel

#### Investigation Phase

1. **Collect Evidence**
   ```powershell
   # Create incident backup
   python -c "from console.backup_restore import get_backup_manager; bm = get_backup_manager(); print(bm.create_backup('Incident-$(Get-Date -Format yyyyMMdd-HHmmss)'))"
   
   # Export logs
   Copy-Item logs\*.log incident_evidence\
   
   # Export configuration
   Copy-Item config.yaml incident_evidence\
   
   # System information
   Get-ComputerInfo > incident_evidence\system_info.txt
   ```

2. **Root Cause Analysis**
   - Review logs for error patterns
   - Check configuration changes
   - Analyze performance metrics
   - Review recent deployments

3. **Solution Implementation**
   - Apply fixes based on root cause
   - Test fixes in isolated environment
   - Implement monitoring for similar issues

#### Recovery Procedures

1. **Service Recovery**
   ```powershell
   # Stop service gracefully
   Stop-Service -Name "WatchLockAI_Sentinel"
   
   # Clear problematic state (if needed)
   Remove-Item data\temp\* -Force
   
   # Restore from backup (if needed)
   # [Use backup procedures above]
   
   # Start service
   Start-Service -Name "WatchLockAI_Sentinel"
   
   # Verify recovery
   python tools\self_check.py --verbose
   ```

2. **Data Recovery**
   - Restore from most recent backup
   - Validate data integrity
   - Reconcile any data loss
   - Update stakeholders on recovery status

3. **Security Incident Recovery**
   - Rotate all credentials
   - Apply security patches
   - Review access logs
   - Implement additional security measures

## Maintenance Procedures

### Scheduled Maintenance Windows

#### Monthly Maintenance (First Saturday, 2-4 AM)

```powershell
# 1. Create pre-maintenance backup
python -c "from console.backup_restore import get_backup_manager; bm = get_backup_manager(); print(bm.create_backup('Pre-maintenance-$(Get-Date -Format yyyyMMdd)'))"

# 2. Update system packages
pip install --upgrade -r requirements.txt

# 3. Rotate secrets
python tools\rotate_secrets.py --action execute

# 4. Clean old logs
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

# 5. Run security scan
python tools\sec_lint.py --output security_scan_$(Get-Date -Format yyyyMMdd).json

# 6. Restart service
Restart-Service -Name "WatchLockAI_Sentinel"

# 7. Post-maintenance validation
python tools\self_check.py --verbose
```

#### Quarterly Maintenance

- Full system backup and restore test
- Performance baseline update
- Security assessment
- Configuration review and cleanup
- Hardware health check
- Documentation updates

### Configuration Management

#### Configuration Backup

```powershell
# Backup current configuration
python tools\config_migrate.py --backup --output config_backup_$(Get-Date -Format yyyyMMdd).json
```

#### Configuration Validation

```powershell
# Validate configuration syntax
python tools\config_migrate.py --validate-file config.yaml

# Check for security issues
python tools\sec_lint.py --path config.yaml
```

#### Configuration Deployment

```powershell
# 1. Validate new configuration
python tools\config_migrate.py --validate-file new_config.yaml

# 2. Backup current configuration
copy config.yaml config.yaml.backup

# 3. Deploy new configuration
copy new_config.yaml config.yaml

# 4. Test configuration
python tools\self_check.py

# 5. Restart service
Restart-Service -Name "WatchLockAI_Sentinel"

# 6. Verify deployment
curl http://localhost:8080/api/metrics/health
```

### Log Management

#### Log Rotation Configuration

```python
# Configure log rotation (in environment)
$env:LOG_MAX_BYTES = "10485760"    # 10MB
$env:LOG_BACKUPS = "10"           # Keep 10 backup files
$env:LOG_REDACT_SECRETS = "1"     # Enable secret redaction
```

#### Manual Log Cleanup

```powershell
# Remove logs older than 30 days
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

# Compress old logs
forfiles /p logs /s /m *.log.* /d -7 /c "cmd /c powershell Compress-Archive @path @path.zip; del @path"
```

## Troubleshooting Guide

### Common Issues

#### Service Won't Start

**Symptoms:** Service fails to start, immediate shutdown

**Diagnosis:**
```powershell
# Check Windows Event Log
Get-WinEvent -LogName Application -MaxEvents 50 | Where-Object {$_.ProviderName -eq "WatchLockAI_Sentinel"}

# Check application logs
Get-Content logs\sentinel.log -Tail 100

# Validate configuration
python tools\config_migrate.py --validate-file config.yaml
```

**Solutions:**
1. Fix configuration errors
2. Check file permissions
3. Verify Python dependencies
4. Review Windows Event Log

#### High Memory Usage

**Symptoms:** Memory usage > 2GB, slow performance

**Diagnosis:**
```powershell
# Check memory usage
Get-Process -Name "python" | Select-Object ProcessName, WorkingSet, PagedMemorySize

# Check for memory leaks in logs
Select-String -Path logs\sentinel.log -Pattern "memory|leak|oom"
```

**Solutions:**
1. Restart service to clear memory
2. Reduce event processing rate
3. Check for memory leaks in custom rules
4. Increase system memory

#### API Not Responding

**Symptoms:** HTTP timeouts, 500 errors

**Diagnosis:**
```powershell
# Test API endpoints
curl -v http://localhost:8080/api/metrics/health

# Check API logs
Select-String -Path logs\sentinel.log -Pattern "api|http|error"

# Test network connectivity
Test-NetConnection -ComputerName localhost -Port 8080
```

**Solutions:**
1. Restart web service component
2. Check firewall settings
3. Verify port availability
4. Review API configuration

#### Authentication Failures

**Symptoms:** 403 Forbidden errors, login failures

**Diagnosis:**
```powershell
# Check authentication configuration
$env:ADMIN_AUTH_ENABLED
$env:ADMIN_TOKEN

# Test with known good credentials
curl -H "X-Admin-Token: $env:ADMIN_TOKEN" http://localhost:8080/api/admin/config/reload
```

**Solutions:**
1. Verify admin token configuration
2. Rotate credentials if compromised
3. Check session key validity
4. Review authentication logs

### Performance Troubleshooting

#### Slow Event Processing

```powershell
# Check event bus metrics
curl http://localhost:8080/api/metrics/event_bus

# Monitor CPU usage
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 5 -MaxSamples 12

# Check disk I/O
Get-Counter "\PhysicalDisk(_Total)\Disk Reads/sec", "\PhysicalDisk(_Total)\Disk Writes/sec"
```

#### Database Performance

```powershell
# Check file system performance
Get-Counter "\LogicalDisk(C:)\Avg. Disk sec/Read", "\LogicalDisk(C:)\Avg. Disk sec/Write"

# Monitor data directory size
Get-ChildItem data -Recurse | Measure-Object -Property Length -Sum
```

### Network Troubleshooting

#### Connectivity Issues

```powershell
# Test internal connectivity
Test-NetConnection -ComputerName localhost -Port 8080

# Check listening ports
netstat -an | findstr 8080

# Test external connectivity (if needed)
Test-NetConnection -ComputerName threat-intel-api.example.com -Port 443
```

## Data Retention & Cleanup

### P5-002: Data Retention Management

#### Enable Retention System

```powershell
# Enable data retention features
$env:RETENTION_ENABLED = "1"
$env:RETENTION_DAYS = "14"  # Keep files for 14 days
```

#### Manual Retention Run

```powershell
# Dry run to see what would be removed
curl -X POST -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/retention/run?dry=true&retention_days=14"

# Execute retention cleanup
curl -X POST -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/retention/run?dry=false&retention_days=14"
```

#### Scheduled Retention

```powershell
# Create scheduled task for daily retention
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"curl -X POST -H 'X-Admin-Token: your-token' 'http://localhost:8080/api/admin/retention/run?dry=false'`""
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
Register-ScheduledTask -TaskName "WatchLockAI_Retention" -Action $action -Trigger $trigger -Description "Daily retention cleanup"
```

#### Directory Statistics

```powershell
# Check retention directory statistics
curl -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/retention/stats"
```

### Data Retention Policies

- **Quarantine Files:** 30 days retention (RETENTION_DAYS + 16)
- **Export Files:** 7 days retention (RETENTION_DAYS - 7)  
- **Log Files:** 14 days retention (RETENTION_DAYS)
- **Anomaly State:** 30 days retention (RETENTION_DAYS + 16)

## Performance Testing & Monitoring

### P5-005: Performance Probes

#### Enable Performance Testing

```powershell
# Enable performance probe functionality
$env:PERF_PROBE_ENABLED = "1"
$env:ADMIN_AUTH_ENABLED = "1"
$env:ADMIN_TOKEN = "your-secure-admin-token"
```

#### Quick Performance Check

```powershell
# Run quick performance assessment
curl -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/perf/quick"
```

#### Detailed Performance Test

```powershell
# Custom performance test
curl -X POST -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/perf/probe?clients=10&duration_s=30&endpoint=/api/metrics/health"
```

#### Stress Testing

```powershell
# High-load stress test
curl -X POST -H "X-Admin-Token: your-token" "http://localhost:8080/api/admin/perf/probe?clients=50&duration_s=60&endpoint=/api/metrics/health"
```

### Performance Benchmarks

#### Baseline Expectations

- **Response Time:** < 100ms (95th percentile)
- **Throughput:** > 100 RPS for health endpoint
- **Success Rate:** > 99% under normal load
- **Concurrent Users:** 50+ without degradation

#### Performance Grading

- **Excellent:** <100ms avg, >95% success rate
- **Good:** <200ms avg, >90% success rate  
- **Fair:** <500ms avg, >80% success rate
- **Poor:** >500ms avg or <80% success rate

### Scheduled Performance Testing

```powershell
# Weekly performance baseline check
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"curl -H 'X-Admin-Token: your-token' 'http://localhost:8080/api/admin/perf/quick' | Out-File -Append 'logs/performance_weekly.log'`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "06:00AM"
Register-ScheduledTask -TaskName "WatchLockAI_PerfCheck" -Action $action -Trigger $trigger
```

## Offline Installation & Deployment

### P5-004: Offline Bundle Creation

#### Create Offline Bundle

```powershell
# Create offline installation bundle
cd C:\WatchLockAI_Sentinel
.\scripts\make_offline_bundle.ps1 -OutputPath "WatchLockAI_Sentinel_Offline.zip" -Verbose
```

#### Bundle Contents

- **Source Code:** Complete application source
- **Virtual Environment:** Pre-configured Python environment with dependencies
- **Bootstrap Script:** Automated installation script
- **Configuration Templates:** Example configurations
- **Documentation:** Operations and deployment guides

#### Deploy from Offline Bundle

```powershell
# Extract bundle
Expand-Archive -Path "WatchLockAI_Sentinel_Offline.zip" -DestinationPath "C:\WatchLockAI_Offline"

# Navigate to bundle
cd C:\WatchLockAI_Offline

# Run bootstrap (basic installation)
.\bootstrap_venv.ps1

# Run bootstrap with service installation
.\bootstrap_venv.ps1 -InstallService

# Run bootstrap skipping tests
.\bootstrap_venv.ps1 -SkipTests -InstallService
```

### Air-Gapped Deployment

#### Prerequisites

- Windows 10/11 or Windows Server 2016+
- PowerShell 5.1+
- Administrator privileges
- Offline bundle file

#### Installation Steps

1. **Transfer Bundle:** Copy bundle to target system via approved media
2. **Extract:** Unzip bundle to deployment directory
3. **Execute Bootstrap:** Run bootstrap script with appropriate flags
4. **Configure:** Edit .env file for environment-specific settings
5. **Validate:** Run verification checks
6. **Start Service:** Enable and start the Windows service

#### Post-Installation Validation

```powershell
# Verify installation
cd source
python tools\verify_minimax_claims.py

# Test self-check
python tools\self_check.py --verbose

# Check service status
Get-Service -Name "WatchLockAI_Sentinel"
```

## Emergency Procedures

### Emergency Shutdown

```powershell
# Immediate service stop
Stop-Service -Name "WatchLockAI_Sentinel" -Force

# Kill all related processes (if needed)
Get-Process -Name "python" | Where-Object {$_.Path -like "*WatchLockAI*"} | Stop-Process -Force

# Disable service startup
Set-Service -Name "WatchLockAI_Sentinel" -StartupType Disabled
```

### Emergency Recovery

```powershell
# 1. Stop all processes
Stop-Service -Name "WatchLockAI_Sentinel" -Force

# 2. Backup current state
Copy-Item -Recurse data data_emergency_$(Get-Date -Format yyyyMMdd_HHmmss)

# 3. Restore from known good backup
# [Use backup procedures]

# 4. Reset to factory defaults (if needed)
Copy-Item config.yaml.template config.yaml

# 5. Clear temporary data
Remove-Item data\temp\* -Force -Recurse
Remove-Item logs\*.log

# 6. Start service
Set-Service -Name "WatchLockAI_Sentinel" -StartupType Automatic
Start-Service -Name "WatchLockAI_Sentinel"

# 7. Verify recovery
python tools\self_check.py --verbose
```

### Security Incident Response

```powershell
# 1. Immediate containment
Stop-Service -Name "WatchLockAI_Sentinel"

# 2. Preserve evidence
Copy-Item -Recurse . security_incident_$(Get-Date -Format yyyyMMdd_HHmmss)

# 3. Rotate all credentials
$env:ROTATE_ENABLED = "1"
python tools\rotate_secrets.py --action execute

# 4. Apply security patches
# [Update system and dependencies]

# 5. Review and harden configuration
python tools\sec_lint.py --fail-on-high

# 6. Restart with monitoring
Start-Service -Name "WatchLockAI_Sentinel"

# 7. Enhanced monitoring
# [Implement additional security monitoring]
```

### Contact Information

- **Operations Team:** ops@watchlockai.com
- **Security Team:** security@watchlockai.com
- **Emergency Hotline:** +1-555-WATCH-AI
- **Escalation Manager:** ops-manager@watchlockai.com

### Documentation References

- **API Documentation:** `/api/docs`
- **Configuration Guide:** `DOCS/config/keys.md`
- **Security Policies:** `DOCS/security/threat_model.md`
- **Architecture Guide:** `DOCS/architecture.md`
- **Deployment Guide:** `DOCS/deploy_windows.md`

## RBAC Flow Diagram

### Admin Authentication & Authorization Flow

The following diagram illustrates the Role-Based Access Control (RBAC) flow for administrative endpoints:

![Admin RBAC Flow](diagrams/admin_rbac_flow.png)

#### Authentication Methods

1. **Session-Based Authentication** (Primary)
   - Uses HTTP session cookies with secure attributes
   - Cookie must include: HttpOnly, Secure (HTTPS), SameSite=Lax/Strict
   - Session timeout: ≤24 hours from issuance
   - Automatic logout clears cookies (Max-Age=0)

2. **Token-Based Authentication** (Fallback)
   - Uses X-Admin-Token header
   - Token must be securely generated and stored
   - Supports both standalone and dual-auth modes

#### Authorization Levels

- **No Auth Required:** When ADMIN_AUTH_ENABLED=0 (development only)
- **Admin User Session:** Valid session + admin role
- **Valid Admin Token:** Correct X-Admin-Token header
- **Rate Limited:** All admin operations subject to rate limiting

#### Security Features

- **Dual Authentication:** Supports both session and token auth
- **Graceful Fallback:** Session auth falls back to token auth
- **Rate Limiting:** Prevents brute force attacks
- **Audit Logging:** All admin actions logged
- **Secure Defaults:** All features default OFF for security

---

**Document Classification:** Confidential  
**Review Schedule:** Quarterly  
**Next Review:** 2025-12-05  
**Approval:** Operations Manager, Security Team Lead
