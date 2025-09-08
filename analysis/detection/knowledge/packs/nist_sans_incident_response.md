# NIST & SANS Incident Response Framework

## NIST Computer Security Incident Handling Guide

### NIST SP 800-61 Rev. 2 Overview

The National Institute of Standards and Technology (NIST) provides comprehensive guidance for establishing and operating computer security incident response capabilities. This framework is widely adopted across government and private sector organizations.

### NIST Incident Response Lifecycle

#### Phase 1: Preparation

**Objective**: Establish the foundation for an effective incident response capability

**Key Activities**:
- **Policy Development**: Create incident response policies and procedures
- **Team Formation**: Establish incident response team with defined roles and responsibilities
- **Training and Awareness**: Provide regular training for incident response team members
- **Tool Acquisition**: Procure and configure incident response tools and technologies
- **Communication Plans**: Develop internal and external communication procedures

**Deliverables**:
- Incident response policy and procedures
- Incident response team charter and contact information
- Training materials and schedules
- Tool inventory and configuration documentation
- Communication templates and contact lists

#### Phase 2: Detection and Analysis

**Objective**: Accurately identify and analyze security incidents

**Key Activities**:
- **Event Monitoring**: Continuous monitoring of security events and alerts
- **Incident Classification**: Categorize and prioritize security incidents
- **Evidence Collection**: Gather and preserve digital evidence
- **Impact Assessment**: Determine the scope and impact of the incident
- **Notification**: Alert appropriate stakeholders and authorities

**Incident Categories**:
- Denial of Service (DoS) attacks
- Malicious code infections
- Unauthorized access incidents
- Inappropriate usage violations
- Multiple component incidents

**Analysis Techniques**:
- Log analysis and correlation
- Network traffic analysis
- Host forensics and memory analysis
- Malware analysis and reverse engineering
- Timeline construction and event correlation

#### Phase 3: Containment, Eradication, and Recovery

**Objective**: Minimize damage and restore normal operations

**Containment Strategies**:
- **Short-term Containment**: Immediate actions to prevent further damage
- **Long-term Containment**: Sustainable measures to maintain business operations
- **Evidence Preservation**: Ensure digital evidence integrity throughout containment

**Eradication Activities**:
- Remove malware and malicious artifacts
- Disable compromised user accounts
- Apply security patches and fixes
- Improve security controls and defenses

**Recovery Operations**:
- Restore systems from known-good backups
- Monitor systems for signs of weakness or compromise
- Implement additional monitoring and logging
- Gradually return systems to production

#### Phase 4: Post-Incident Activity

**Objective**: Learn from incidents and improve response capabilities

**Key Activities**:
- **Lessons Learned Meeting**: Conduct formal review of incident response
- **Documentation Updates**: Update policies, procedures, and documentation
- **Evidence Retention**: Properly store or dispose of evidence
- **Legal Coordination**: Support legal proceedings if necessary

## SANS Incident Response Methodology

### SANS Six-Step Process

The SANS Institute has developed a complementary six-step incident response process that provides additional tactical guidance for incident responders.

#### Step 1: Preparation

**Focus Areas**:
- Incident response team development
- Policy and procedure creation
- Tool and technology preparation
- Training and awareness programs

**Key Considerations**:
- Define incident types and severity levels
- Establish escalation procedures and decision trees
- Create incident response kits and toolkits
- Develop communication and notification procedures

#### Step 2: Identification

**Detection Methods**:
- Security monitoring systems and SIEM platforms
- Intrusion detection and prevention systems
- Endpoint detection and response solutions
- User reports and help desk tickets
- Threat intelligence and external notifications

**Identification Criteria**:
- Unusual network traffic patterns
- Unexpected system behavior or performance
- Suspicious file modifications or creations
- Unauthorized user access or privilege escalation
- Known malware signatures or indicators

#### Step 3: Containment

**Containment Principles**:
- Act quickly to prevent further damage
- Preserve evidence for later analysis
- Maintain business continuity where possible
- Document all containment actions taken

**Containment Options**:
- Network isolation and segmentation
- System shutdown or suspension
- User account disabling or password reset
- Malware quarantine and removal
- Traffic blocking and filtering

#### Step 4: Eradication

**Eradication Tasks**:
- Remove malware and malicious files
- Close unauthorized network connections
- Disable compromised user accounts
- Apply security patches and updates
- Reconfigure systems and security controls

**Verification Methods**:
- Anti-malware scanning and analysis
- Vulnerability assessment and testing
- Configuration compliance checking
- Log analysis and review
- System integrity verification

#### Step 5: Recovery

**Recovery Planning**:
- Develop recovery timeline and milestones
- Define success criteria and validation tests
- Plan monitoring and surveillance activities
- Prepare rollback procedures if needed

**Recovery Activities**:
- Restore systems from clean backups
- Apply security patches and configurations
- Test system functionality and performance
- Monitor for signs of compromise
- Gradually restore normal operations

#### Step 6: Lessons Learned

**Review Process**:
- Schedule lessons learned meeting within one week
- Include all stakeholders and participants
- Document findings and recommendations
- Update policies, procedures, and training materials

**Improvement Areas**:
- Response time and effectiveness
- Communication and coordination
- Tool and technology performance
- Training and awareness needs
- Policy and procedure gaps

## Incident Classification and Prioritization

### NIST Incident Categories

#### Category 1: Denial of Service
- Network-based DoS attacks
- Application-layer attacks
- Distributed denial of service (DDoS)
- Resource exhaustion attacks

#### Category 2: Malicious Code
- Virus and worm infections
- Trojan horse and backdoor installations
- Rootkit and bootkit infections
- Potentially unwanted programs (PUPs)

#### Category 3: Unauthorized Access
- Successful system intrusions
- Privilege escalation attacks
- Account compromise and abuse
- Remote access trojan infections

#### Category 4: Inappropriate Usage
- Policy violation incidents
- Unauthorized software installation
- Personal use of corporate resources
- Data misuse and inappropriate sharing

### Severity Levels and Response Times

#### High Severity (Critical Impact)
- **Response Time**: 1 hour
- **Characteristics**: Mission-critical systems affected, significant data loss risk
- **Examples**: Ransomware infections, data breaches, critical system compromises

#### Medium Severity (Moderate Impact)
- **Response Time**: 4 hours  
- **Characteristics**: Important systems affected, limited operational impact
- **Examples**: Malware infections, unauthorized access attempts, policy violations

#### Low Severity (Minimal Impact)
- **Response Time**: 8 hours
- **Characteristics**: Non-critical systems affected, minimal operational impact
- **Examples**: Failed intrusion attempts, minor policy violations, suspicious activities

## Integration with Business Continuity

### Business Impact Analysis
- Identify critical business processes and assets
- Assess recovery time objectives (RTO) and recovery point objectives (RPO)
- Determine acceptable downtime and data loss thresholds
- Map incident types to business impact levels

### Continuity Planning
- Develop alternate operating procedures
- Establish backup communication channels
- Create alternate work locations and arrangements
- Maintain vendor and supplier contact information

### Crisis Management
- Define crisis escalation procedures
- Establish crisis communication protocols
- Coordinate with legal, public relations, and executive teams
- Manage media and stakeholder communications

## Legal and Regulatory Considerations

### Evidence Handling
- Maintain chain of custody documentation
- Follow forensically sound collection procedures
- Preserve evidence integrity and admissibility
- Coordinate with law enforcement when appropriate

### Regulatory Compliance
- Understand industry-specific requirements
- Meet notification and reporting obligations
- Maintain required documentation and records
- Coordinate with regulators and compliance teams

### Privacy Protection
- Protect personal and sensitive information
- Follow data breach notification requirements
- Implement privacy-protective investigation methods
- Coordinate with privacy and legal teams

---

# --- sentinel:directive ---
component: threat_intelligence
provides:
  framework: "NIST SP 800-61 & SANS IR Methodology"
  nist_phases: ["preparation", "detection_and_analysis", "containment_eradication_recovery", "post_incident_activity"]
  sans_steps: ["preparation", "identification", "containment", "eradication", "recovery", "lessons_learned"]
  coverage: "incident_response_lifecycle"
constraints:
  update_frequency: "annually"
  source_authority: "nist.gov, sans.org"
  last_updated: "2025-09-02"
# --- end ---
