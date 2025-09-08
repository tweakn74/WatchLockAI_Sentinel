# UX Grounding and Terminology Framework

## Industry Research Foundation

This document outlines the terminology and user experience patterns that inform WatchLockAI's interface design, inspired by industry leaders while maintaining our original visual language.

## Core EDR Terminology

### Primary Concepts
- **Detections**: Security events identified by analysis engines requiring investigation
- **Hosts**: Monitored endpoints/devices within the protected environment  
- **Policies**: Configurable rules and settings governing monitoring behavior
- **Incidents**: Confirmed security events requiring response action
- **Assets**: Physical and logical resources under protection

### Monitoring Categories
- **File System Monitoring**: Real-time tracking of file operations and changes
- **Process Monitoring**: Surveillance of running applications and system processes
- **Registry Monitoring**: Windows registry change detection and analysis
- **Network Monitoring**: Connection and traffic pattern analysis
- **Account Activity**: User authentication and privilege change tracking

### Response Actions
- **Network Containment**: Isolating compromised endpoints from network access
- **Process Termination**: Stopping malicious or suspicious processes
- **File Quarantine**: Securing potentially harmful files for analysis
- **Alert Generation**: Notifying security teams of critical events

## UI Information Architecture

### Dashboard Structure
- **Overview Dashboard**: High-level security posture and key metrics
- **Detections View**: Filterable list of security events with investigation tools
- **Asset Monitoring**: Real-time status of protected endpoints and resources
- **Account Activity**: User behavior analysis and authentication events
- **Script & Process**: Execution monitoring and behavioral analysis

### Visual Language Principles
- **Status Indicators**: Green (secure), Yellow (attention), Red (critical)
- **Temporal Context**: Recent events prominently displayed with time-based filtering
- **Drill-down Navigation**: From summary views to detailed investigation panels
- **Action-oriented Design**: Clear response options for each detection type

## Original Implementation Notes

While inspired by industry leaders like CrowdStrike Falcon, WatchLockAI implements these concepts through:
- Local-first architecture with privacy by default
- RAG-enhanced detection rationale and explanations
- Simplified deployment for small to medium organizations
- Windows-first design optimized for local environments

---
*Research conducted: September 1, 2025*  
*Sources: Public CrowdStrike documentation and industry best practices*  
*Usage: Inspiration only - all implementations are original*