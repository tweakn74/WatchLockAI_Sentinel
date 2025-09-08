# MITRE ATT&CK Framework v17.0

## Reconnaissance (TA0043)

### T1592 - Gather Victim Host Information
Adversaries may gather information about the victim's hosts that can be used during targeting. Information about hosts may include a variety of details, including administrative data (ex: name, assigned IP, functionality, etc.) as well as specifics regarding its configuration (ex: operating system, language, etc.).

**Platforms**: Windows, macOS, Linux, Network
**Data Sources**: Network Traffic, Internet Scan
**Detection**: Monitor for suspicious network scanning activities and information gathering attempts.

### T1589 - Gather Victim Identity Information
Adversaries may gather information about the victim's identity that can be used during targeting. Information about identities may include a variety of details, including personal data (ex: employee names, email addresses, etc.) as well as sensitive details such as credentials.

**Platforms**: Pre-Attack
**Data Sources**: Social Media, Public Information
**Detection**: Monitor for unusual information gathering activities targeting organizational personnel.

## Initial Access (TA0001)

### T1566 - Phishing
Adversaries may send phishing messages to gain access to victim systems. All forms of phishing are electronically delivered social engineering attacks that aim to collect sensitive information, credentials, or execute malicious code.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: Spearphishing Attachment (T1566.001), Spearphishing Link (T1566.002), Spearphishing via Service (T1566.003)
**Detection**: Monitor for suspicious email patterns, unexpected attachments, and social engineering indicators.

### T1078 - Valid Accounts
Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.

**Platforms**: Windows, macOS, Linux, Network
**Sub-techniques**: Default Accounts (T1078.001), Domain Accounts (T1078.002), Local Accounts (T1078.003), Cloud Accounts (T1078.004)
**Detection**: Monitor for unusual login patterns, off-hours access, and credential abuse indicators.

## Execution (TA0002)

### T1059 - Command and Scripting Interpreter
Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways of interacting with computer systems and are a common feature across many different platforms.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: PowerShell (T1059.001), AppleScript (T1059.002), Windows Command Shell (T1059.003), Unix Shell (T1059.004), Visual Basic (T1059.005), Python (T1059.006), JavaScript (T1059.007), Network Device CLI (T1059.008), Cloud API (T1059.009)
**Detection**: Monitor for process execution of scripting engines and command-line interpreters with unusual command-line arguments.

### T1106 - Native API
Adversaries may interact with the native OS application programming interface (API) to execute behaviors. Native APIs provide a controlled means of calling low-level OS services within the kernel.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor API calls for unusual patterns, frequency, and context that may indicate malicious usage.

## Persistence (TA0003)

### T1053 - Scheduled Task/Job
Adversaries may abuse task scheduling functionality to facilitate initial or recurring execution of malicious code. Utilities exist within all major operating systems to schedule programs or scripts to be executed at a specified date and time.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: At (T1053.001), Cron (T1053.003), Systemd Timers (T1053.006), Windows Task Scheduler (T1053.005)
**Detection**: Monitor scheduled task/job creation and modification for suspicious activities.

### T1547 - Boot or Logon Autostart Execution
Adversaries may configure system settings to automatically execute a program during system boot or logon to maintain persistence or gain higher-level privileges on compromised systems.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: Registry Run Keys (T1547.001), Startup Items (T1547.005), Kernel Modules and Extensions (T1547.006), Re-opened Applications (T1547.007), LSASS Driver (T1547.008), Shortcut Modification (T1547.009), Port Monitors (T1547.010), Plist Modification (T1547.011), Print Processors (T1547.012), XDG Autostart Entries (T1547.013), Active Setup (T1547.014), Login Items (T1547.015)
**Detection**: Monitor registry modifications, startup folder changes, and system configuration alterations.

## Privilege Escalation (TA0004)

### T1134 - Access Token Manipulation
Adversaries may modify access tokens to operate under a different user or system security context to perform actions and bypass access controls.

**Platforms**: Windows
**Sub-techniques**: Token Impersonation/Theft (T1134.001), Create Process with Token (T1134.002), Make and Impersonate Token (T1134.003), Parent PID Spoofing (T1134.004), SID-History Injection (T1134.005)
**Detection**: Monitor for unusual token usage patterns and privilege escalation attempts.

### T1068 - Exploitation for Privilege Escalation
Adversaries may exploit software vulnerabilities in an attempt to elevate privileges. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for exploitation attempts and unusual privilege escalation behaviors.

## Defense Evasion (TA0005)

### T1055 - Process Injection
Adversaries may inject code into processes in order to evade process-based defenses as well as possibly elevate privileges. Process injection is a method of executing arbitrary code in the address space of a separate live process.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: Dynamic-link Library Injection (T1055.001), Portable Executable Injection (T1055.002), Thread Execution Hijacking (T1055.003), Asynchronous Procedure Call (T1055.004), Thread Local Storage (T1055.005), Ptrace System Calls (T1055.008), Proc Memory (T1055.009), Extra Window Memory Injection (T1055.011), Process Hollowing (T1055.012), Process Doppelgänging (T1055.013), VDSO Hijacking (T1055.014), ListPlanting (T1055.015)
**Detection**: Monitor for suspicious process behavior, memory modifications, and injection techniques.

### T1027 - Obfuscated Files or Information
Adversaries may attempt to make an executable or file difficult to discover or analyze by encrypting, encoding, or otherwise obfuscating its contents on the system or in transit.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: Binary Padding (T1027.001), Software Packing (T1027.002), Steganography (T1027.003), Compile After Delivery (T1027.004), Indicator Removal from Tools (T1027.005), HTML Smuggling (T1027.006), Dynamic API Resolution (T1027.007), Stripped Payloads (T1027.008), Embedded Payloads (T1027.009), Command Obfuscation (T1027.010), Fileless Storage (T1027.011)
**Detection**: Analyze files for obfuscation techniques and monitor for unusual encoding/encryption activities.

## Credential Access (TA0006)

### T1003 - OS Credential Dumping
Adversaries may attempt to dump credentials to obtain account login and credential material, normally in the form of a hash or a clear text password, from the operating system and software.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: LSASS Memory (T1003.001), Security Account Manager (T1003.002), NTDS (T1003.003), LSA Secrets (T1003.004), Cached Domain Credentials (T1003.005), DCSync (T1003.006), Proc Filesystem (T1003.007), /etc/passwd and /etc/shadow (T1003.008)
**Detection**: Monitor for process access to sensitive credential stores and memory dumps.

### T1110 - Brute Force
Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.

**Platforms**: Windows, macOS, Linux, Network, Office 365, SaaS, IaaS, Google Workspace, Azure AD
**Sub-techniques**: Password Guessing (T1110.001), Password Cracking (T1110.002), Password Spraying (T1110.003), Credential Stuffing (T1110.004)
**Detection**: Monitor for multiple failed authentication attempts and suspicious login patterns.

## Discovery (TA0007)

### T1083 - File and Directory Discovery
Adversaries may enumerate files and directories or may search in specific locations of a host or network share for certain information within a file system.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for unusual file and directory enumeration activities using native OS commands.

### T1057 - Process Discovery
Adversaries may attempt to get information about running processes on a system. Information obtained could be used to gain an understanding of common software/applications running on systems within the network.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for process enumeration commands and suspicious system reconnaissance.

## Collection (TA0009)

### T1005 - Data from Local System
Adversaries may search local system sources, such as file systems and configuration files or local databases, to find files of interest and sensitive data prior to Exfiltration.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for unusual file access patterns and data collection activities.

### T1113 - Screen Capture
Adversaries may attempt to take screen captures of the desktop to gather information over the course of an operation. Screen capturing functionality may be incorporated into the remote access tools used by the adversary.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for screen capture API calls and suspicious screenshot activities.

## Command and Control (TA0011)

### T1071 - Application Layer Protocol
Adversaries may communicate using OSI application layer protocols to avoid detection/network filtering by blending in with existing traffic.

**Platforms**: Windows, macOS, Linux, Network
**Sub-techniques**: Web Protocols (T1071.001), File Transfer Protocols (T1071.002), Mail Protocols (T1071.003), DNS (T1071.004)
**Detection**: Analyze network traffic for unusual protocol usage and communication patterns.

### T1573 - Encrypted Channel
Adversaries may employ a known encryption algorithm to conceal command and control traffic rather than relying on any inherent protections provided by a communication protocol.

**Platforms**: Windows, macOS, Linux, Network
**Sub-techniques**: Symmetric Cryptography (T1573.001), Asymmetric Cryptography (T1573.002)
**Detection**: Monitor for encrypted communication channels and analyze traffic patterns.

## Exfiltration (TA0010)

### T1041 - Exfiltration Over C2 Channel
Adversaries may steal data by exfiltrating it over an existing command and control channel. Stolen data is encoded into the normal communications channel using the same protocol as command and control communications.

**Platforms**: Windows, macOS, Linux, Network
**Detection**: Monitor for unusual data volumes and patterns in command and control communications.

### T1048 - Exfiltration Over Alternative Protocol
Adversaries may steal data by exfiltrating it over a different protocol than that of the existing command and control channel.

**Platforms**: Windows, macOS, Linux, Network
**Sub-techniques**: Exfiltration Over DNS (T1048.003)
**Detection**: Monitor for data exfiltration over unusual protocols and channels.

## Impact (TA0040)

### T1486 - Data Encrypted for Impact
Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources. They can attempt to render stored data inaccessible by encrypting files or data on local and remote drives.

**Platforms**: Windows, macOS, Linux
**Detection**: Monitor for file encryption activities, ransomware behavior patterns, and unusual file modifications.

### T1490 - Inhibit System Recovery
Adversaries may delete or remove built-in operating system data and turn off services designed to aid in the recovery of a corrupted system to prevent recovery.

**Platforms**: Windows, macOS, Linux
**Sub-techniques**: Inhibit System Recovery (T1490.001)
**Detection**: Monitor for deletion of backup files, recovery tools, and system restore functionality.

---

# --- sentinel:directive ---
component: threat_intelligence
provides:
  framework: "MITRE ATT&CK Enterprise v17.0"
  tactics: ["reconnaissance", "initial_access", "execution", "persistence", "privilege_escalation", "defense_evasion", "credential_access", "discovery", "collection", "command_and_control", "exfiltration", "impact"]
  techniques_count: 195
  coverage: "enterprise_tactics"
constraints:
  update_frequency: "quarterly"
  source_authority: "mitre.org"
  last_updated: "2025-09-02"
# --- end ---
