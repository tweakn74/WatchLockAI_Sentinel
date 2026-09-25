# Lockheed Martin Cyber Kill Chain

## Overview

The Cyber Kill Chain is a framework developed by Lockheed Martin that identifies the stages of a cyber attack. Understanding these phases helps defenders identify and stop attacks at each stage, rather than waiting for the final payload delivery.

## Phase 1: Reconnaissance

### Description
Research, identification and selection of targets, often represented as crawling Internet websites such as conference proceedings and mailing lists for email addresses, social relationships, or information on specific technologies.

### Adversary Activities
- Harvesting email addresses, conference information, etc.
- WHOIS queries on domains
- Social media profiling and social engineering research
- Port scanning and network reconnaissance
- DNS enumeration and subdomain discovery

### Detection Opportunities
- Monitor for suspicious network reconnaissance activities
- Analyze unusual DNS queries and WHOIS lookups
- Track social engineering attempts and information gathering
- Detect automated scanning patterns

### Defensive Measures
- Limit information disclosure in public forums
- Monitor and analyze inbound network reconnaissance
- Implement deception technologies (honeypots, honeynets)
- Social media awareness training

## Phase 2: Weaponization

### Description
Coupling a remote access trojan with an exploit into a deliverable payload, typically by means of an automated tool (weaponizer). Increasingly, client application data files such as Adobe Portable Document Format (PDF) or Microsoft Office documents serve as the weaponized deliverable.

### Adversary Activities
- Malware development and customization
- Exploit kit preparation
- Document weaponization (PDF, Office files)
- Zero-day exploit integration
- Command and control infrastructure preparation

### Detection Opportunities
- File hash analysis and threat intelligence correlation
- Behavioral analysis of suspicious documents
- Static and dynamic malware analysis
- Anomaly detection in document processing

### Defensive Measures
- Application sandboxing and isolation
- Document security policies and controls
- Advanced threat protection solutions
- Regular patching and vulnerability management

## Phase 3: Delivery

### Description
Transmission of the weapon to the targeted environment. The three most prevalent delivery vectors for weaponized payloads by APT actors, as observed by the Mandiant M-Trends report, are email attachments, websites, and USB removable media.

### Adversary Activities
- Spear-phishing email campaigns
- Watering hole attacks on websites
- Supply chain compromises
- USB and removable media distribution
- Social engineering and pretexting

### Detection Opportunities
- Email security gateway analysis
- Web proxy and URL filtering
- Network traffic analysis and monitoring
- Endpoint detection of removable media
- User behavior analytics

### Defensive Measures
- Email security solutions and user training
- Web application firewalls and filtering
- Network segmentation and monitoring
- USB and removable media controls
- Security awareness programs

## Phase 4: Exploitation

### Description
After the weapon is delivered to victim host, exploitation triggers intruders' code. Most often, exploitation targets an application or operating system vulnerability, but it could also more simply exploit the users themselves or leverage an operating system feature that auto-executes code.

### Adversary Activities
- Buffer overflow exploitation
- Zero-day vulnerability exploitation
- Social engineering and user manipulation
- Privilege escalation techniques
- Anti-analysis and evasion methods

### Detection Opportunities
- Exploit detection and prevention systems
- Behavioral monitoring and anomaly detection
- Memory protection and control flow integrity
- Application crash analysis and forensics
- System call monitoring

### Defensive Measures
- Vulnerability management and patching
- Exploit prevention technologies (DEP, ASLR)
- Application whitelisting and control
- User access controls and least privilege
- System hardening and configuration management

## Phase 5: Installation

### Description
Installation of a remote access trojan or backdoor on the victim system allows the adversary to maintain persistence inside the environment.

### Adversary Activities
- Backdoor and RAT installation
- Registry modification for persistence
- Scheduled task and service creation
- File system hiding and camouflage
- Communication channel establishment

### Detection Opportunities
- File integrity monitoring
- Registry and system configuration monitoring
- Network communication analysis
- Process and service monitoring
- Persistence mechanism detection

### Defensive Measures
- Host-based intrusion prevention systems
- Application and system integrity monitoring
- Network access controls and segmentation
- Behavioral monitoring and analysis
- Regular system auditing and baselining

## Phase 6: Command and Control (C2)

### Description
Typically, compromised hosts must beacon outbound to an Internet controller server to establish a C2 channel. APT malware especially requires manual interaction rather than conducting activity automatically. Once the C2 channel is established, intruders have "hands on the keyboard" access inside the target environment.

### Adversary Activities
- Command and control server communication
- Remote administration and control
- Data exfiltration preparation
- Lateral movement planning
- Additional tool and malware deployment

### Detection Opportunities
- Network traffic analysis and monitoring
- DNS monitoring and analysis
- Unusual outbound connections
- Communication protocol analysis
- Behavioral network analysis

### Defensive Measures
- Network monitoring and analysis tools
- DNS filtering and monitoring
- Proxy and firewall controls
- Network segmentation and isolation
- Threat intelligence integration

## Phase 7: Actions on Objectives

### Description
Only now, after progressing through the first six phases, can intruders take actions to achieve their original objectives. Typically, this objective is data exfiltration which involves collecting, encrypting and extracting information from the victim environment; violations of data integrity or availability are potential objectives as well.

### Adversary Activities
- Data collection and aggregation
- Credential harvesting and privilege escalation
- Lateral movement and network exploration
- Data exfiltration and theft
- System destruction and disruption

### Detection Opportunities
- Data loss prevention systems
- User and entity behavior analytics
- File access monitoring and auditing
- Network data flow analysis
- Privilege escalation detection

### Defensive Measures
- Data classification and protection
- Access controls and data loss prevention
- Network monitoring and segmentation
- Incident response and forensics
- Business continuity and recovery planning

## Kill Chain Disruption Strategy

### Early Stage Disruption (Phases 1-3)
**Most Cost-Effective**: Preventing reconnaissance, weaponization, and delivery
- Threat intelligence and information sharing
- Employee security awareness training
- Email and web security controls
- Vulnerability management

### Mid-Stage Disruption (Phases 4-5)
**Critical Control Points**: Stopping exploitation and installation
- Exploit prevention technologies
- Application security controls
- Endpoint detection and response
- System hardening

### Late Stage Disruption (Phases 6-7)
**Damage Limitation**: Detecting command/control and actions
- Network monitoring and analysis
- Data loss prevention
- Incident response capabilities
- Forensics and threat hunting

## Integration with MITRE ATT&CK

The Cyber Kill Chain provides a strategic framework that maps well to MITRE ATT&CK tactics:

- **Reconnaissance** -> ATT&CK Reconnaissance (TA0043)
- **Weaponization** -> ATT&CK Resource Development (TA0042)
- **Delivery** -> ATT&CK Initial Access (TA0001)
- **Exploitation** -> ATT&CK Execution (TA0002), Privilege Escalation (TA0004)
- **Installation** -> ATT&CK Persistence (TA0003), Defense Evasion (TA0005)
- **Command & Control** -> ATT&CK Command and Control (TA0011)
- **Actions on Objectives** -> ATT&CK Collection (TA0009), Exfiltration (TA0010), Impact (TA0040)

---

# --- sentinel:directive ---
component: threat_intelligence
provides:
  framework: "Lockheed Martin Cyber Kill Chain"
  phases: ["reconnaissance", "weaponization", "delivery", "exploitation", "installation", "command_and_control", "actions_on_objectives"]
  phase_count: 7
  coverage: "attack_lifecycle"
constraints:
  update_frequency: "annually"
  source_authority: "lockheedmartin.com"
  last_updated: "2025-09-02"
# --- end ---
