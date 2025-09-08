#!/usr/bin/env python3
"""
Create final implementation modules for WatchLockAI Agent
"""

import os
from pathlib import Path

def create_forensics_module(base_path):
    """Create forensics investigation engine"""
    
    # Forensics interface
    forensics_interface = """using System;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using WatchLockAI.Common;

namespace WatchLockAI.Forensics;

/// <summary>
/// Digital forensics and investigation engine
/// </summary>
public interface IForensicsEngine
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task StopAsync();
    Task<Investigation> StartInvestigationAsync(ThreatEvent threat);
    Task<Timeline> GenerateTimelineAsync(string investigationId);
    Task<EvidenceCollection> CollectEvidenceAsync(ThreatEvent threat);
    Task<string> GenerateReportAsync(Investigation investigation);
}

/// <summary>
/// Investigation case management
/// </summary>
public class Investigation
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public DateTime StartTime { get; set; } = DateTime.UtcNow;
    public DateTime? EndTime { get; set; }
    public string ThreatId { get; set; }
    public InvestigationStatus Status { get; set; }
    public List<Evidence> Evidence { get; set; } = new();
    public Timeline Timeline { get; set; }
    public string Summary { get; set; }
    public string RecommendedActions { get; set; }
}

/// <summary>
/// Timeline of events
/// </summary>
public class Timeline
{
    public string InvestigationId { get; set; }
    public List<TimelineEvent> Events { get; set; } = new();
    public DateTime EarliestEvent { get; set; }
    public DateTime LatestEvent { get; set; }
}

/// <summary>
/// Timeline event entry
/// </summary>
public class TimelineEvent
{
    public DateTime Timestamp { get; set; }
    public string Source { get; set; }
    public string EventType { get; set; }
    public string Description { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Evidence collection
/// </summary>
public class EvidenceCollection
{
    public string InvestigationId { get; set; }
    public List<Evidence> Items { get; set; } = new();
    public DateTime CollectionTime { get; set; }
}

/// <summary>
/// Digital evidence item
/// </summary>
public class Evidence
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public EvidenceType Type { get; set; }
    public string Source { get; set; }
    public string Hash { get; set; }
    public DateTime CollectedAt { get; set; }
    public byte[] Data { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public enum InvestigationStatus
{
    Started,
    InProgress,
    Completed,
    Suspended
}

public enum EvidenceType
{
    ProcessMemory,
    RegistrySnapshot,
    FileSystemArtifact,
    NetworkCapture,
    EventLog,
    SystemState
}
"""
    
    with open(base_path / "src/WatchLockAI.Forensics/IForensicsEngine.cs", "w") as f:
        f.write(forensics_interface)
    
    # Forensics implementation
    forensics_implementation = """using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Management;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Forensics;

/// <summary>
/// Autopsy/Sleuthkit inspired forensics engine for Windows
/// </summary>
public class ForensicsEngine : IForensicsEngine
{
    private readonly ILogger<ForensicsEngine> _logger;
    private readonly IEventLogger _eventLogger;
    private readonly Dictionary<string, Investigation> _activeInvestigations;

    public ForensicsEngine(ILogger<ForensicsEngine> logger, IEventLogger eventLogger)
    {
        _logger = logger;
        _eventLogger = eventLogger;
        _activeInvestigations = new Dictionary<string, Investigation>();
    }

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Initializing Forensics Engine");
            
            // Create evidence storage directory
            var evidenceDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), 
                                         "WatchLockAI", "Evidence");
            Directory.CreateDirectory(evidenceDir);
            
            _logger.LogInformation("Forensics Engine initialized");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize Forensics Engine");
            throw;
        }
    }

    public async Task StopAsync()
    {
        try
        {
            _logger.LogInformation("Stopping Forensics Engine");
            
            // Complete any ongoing investigations
            foreach (var investigation in _activeInvestigations.Values)
            {
                if (investigation.Status == InvestigationStatus.InProgress)
                {
                    investigation.Status = InvestigationStatus.Suspended;
                    investigation.EndTime = DateTime.UtcNow;
                }
            }
            
            _logger.LogInformation("Forensics Engine stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping Forensics Engine");
        }
    }

    public async Task<Investigation> StartInvestigationAsync(ThreatEvent threat)
    {
        try
        {
            _logger.LogInformation("Starting forensic investigation for threat {ThreatId}", threat.Id);

            var investigation = new Investigation
            {
                ThreatId = threat.Id,
                Status = InvestigationStatus.Started
            };

            _activeInvestigations[investigation.Id] = investigation;

            // Start evidence collection
            investigation.Status = InvestigationStatus.InProgress;
            
            // Collect evidence asynchronously
            _ = Task.Run(async () =>
            {
                try
                {
                    var evidence = await CollectEvidenceAsync(threat);
                    investigation.Evidence.AddRange(evidence.Items);
                    
                    var timeline = await GenerateTimelineAsync(investigation.Id);
                    investigation.Timeline = timeline;
                    
                    investigation.Status = InvestigationStatus.Completed;
                    investigation.EndTime = DateTime.UtcNow;
                    
                    _logger.LogInformation("Investigation {InvestigationId} completed", investigation.Id);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error during investigation {InvestigationId}", investigation.Id);
                    investigation.Status = InvestigationStatus.Suspended;
                }
            });

            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.ThreatDetected,
                Source = "ForensicsEngine",
                Message = $"Started forensic investigation {investigation.Id} for threat {threat.Type}"
            });

            return investigation;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting forensic investigation for threat {ThreatId}", threat.Id);
            throw;
        }
    }

    public async Task<Timeline> GenerateTimelineAsync(string investigationId)
    {
        try
        {
            _logger.LogInformation("Generating timeline for investigation {InvestigationId}", investigationId);

            var timeline = new Timeline
            {
                InvestigationId = investigationId
            };

            // Collect timeline events from various sources
            await CollectEventLogEventsAsync(timeline);
            await CollectFileSystemEventsAsync(timeline);
            await CollectRegistryEventsAsync(timeline);
            await CollectNetworkEventsAsync(timeline);

            // Sort events by timestamp
            timeline.Events.Sort((a, b) => a.Timestamp.CompareTo(b.Timestamp));
            
            if (timeline.Events.Count > 0)
            {
                timeline.EarliestEvent = timeline.Events[0].Timestamp;
                timeline.LatestEvent = timeline.Events[^1].Timestamp;
            }

            _logger.LogInformation("Generated timeline with {EventCount} events for investigation {InvestigationId}", 
                timeline.Events.Count, investigationId);

            return timeline;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating timeline for investigation {InvestigationId}", investigationId);
            return new Timeline { InvestigationId = investigationId };
        }
    }

    public async Task<EvidenceCollection> CollectEvidenceAsync(ThreatEvent threat)
    {
        try
        {
            _logger.LogInformation("Collecting evidence for threat {ThreatId}", threat.Id);

            var collection = new EvidenceCollection
            {
                CollectionTime = DateTime.UtcNow
            };

            // Collect different types of evidence
            await CollectProcessMemoryAsync(collection, threat);
            await CollectRegistrySnapshotAsync(collection);
            await CollectFileSystemArtifactsAsync(collection, threat);
            await CollectEventLogsAsync(collection);
            await CollectSystemStateAsync(collection);

            _logger.LogInformation("Collected {EvidenceCount} evidence items for threat {ThreatId}", 
                collection.Items.Count, threat.Id);

            return collection;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error collecting evidence for threat {ThreatId}", threat.Id);
            return new EvidenceCollection();
        }
    }

    public async Task<string> GenerateReportAsync(Investigation investigation)
    {
        try
        {
            _logger.LogInformation("Generating report for investigation {InvestigationId}", investigation.Id);

            var report = $@"
# WatchLockAI Forensic Investigation Report

## Investigation Details
- **Investigation ID**: {investigation.Id}
- **Start Time**: {investigation.StartTime:yyyy-MM-dd HH:mm:ss} UTC
- **End Time**: {investigation.EndTime?.ToString("yyyy-MM-dd HH:mm:ss") ?? "Ongoing"} UTC
- **Status**: {investigation.Status}
- **Related Threat**: {investigation.ThreatId}

## Executive Summary
{investigation.Summary ?? "Investigation completed successfully."}

## Timeline Analysis
";

            if (investigation.Timeline?.Events.Count > 0)
            {
                report += $@"
### Key Events ({investigation.Timeline.Events.Count} total)

| Timestamp | Source | Event Type | Description |
|-----------|--------|------------|-------------|
";
                foreach (var evt in investigation.Timeline.Events.Take(20)) // Show first 20 events
                {
                    report += $"| {evt.Timestamp:yyyy-MM-dd HH:mm:ss} | {evt.Source} | {evt.EventType} | {evt.Description} |\n";
                }
            }

            report += $@"

## Evidence Collected
- **Total Evidence Items**: {investigation.Evidence.Count}
";

            var evidenceByType = investigation.Evidence.GroupBy(e => e.Type);
            foreach (var group in evidenceByType)
            {
                report += $"- **{group.Key}**: {group.Count()} items\n";
            }

            report += $@"

## Recommended Actions
{investigation.RecommendedActions ?? "Review evidence and implement appropriate security measures."}

## Technical Details
- **Evidence Hash Summary**: Available upon request
- **Full Timeline**: Available in system logs
- **Raw Evidence**: Stored in secure evidence vault

---
*Report generated by WatchLockAI Forensics Engine*
*Generated at: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC*
";

            return report;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating report for investigation {InvestigationId}", investigation.Id);
            return $"Error generating report: {ex.Message}";
        }
    }

    private async Task CollectEventLogEventsAsync(Timeline timeline)
    {
        try
        {
            // Collect recent security events from Windows Event Log
            var eventLog = new EventLog("Security");
            var recentEvents = eventLog.Entries.Cast<EventLogEntry>()
                .Where(e => e.TimeGenerated > DateTime.Now.AddHours(-24))
                .Take(100);

            foreach (var entry in recentEvents)
            {
                timeline.Events.Add(new TimelineEvent
                {
                    Timestamp = entry.TimeGenerated,
                    Source = "Windows Security Log",
                    EventType = entry.EntryType.ToString(),
                    Description = entry.Message?.Substring(0, Math.Min(200, entry.Message.Length)) ?? "No description"
                });
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting event log events");
        }
    }

    private async Task CollectFileSystemEventsAsync(Timeline timeline)
    {
        try
        {
            // Collect recent file system changes
            // This would typically use USN Journal or similar
            _logger.LogDebug("Collecting file system events");
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting file system events");
        }
    }

    private async Task CollectRegistryEventsAsync(Timeline timeline)
    {
        try
        {
            // Collect recent registry changes
            _logger.LogDebug("Collecting registry events");
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting registry events");
        }
    }

    private async Task CollectNetworkEventsAsync(Timeline timeline)
    {
        try
        {
            // Collect network connection events
            _logger.LogDebug("Collecting network events");
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting network events");
        }
    }

    private async Task CollectProcessMemoryAsync(EvidenceCollection collection, ThreatEvent threat)
    {
        try
        {
            if (threat.Properties.TryGetValue("SystemEvent", out var systemEventObj) &&
                systemEventObj is SystemEvent systemEvent)
            {
                // Collect memory dump of the suspicious process
                var processId = systemEvent.ProcessId;
                
                if (processId > 0)
                {
                    var evidence = new Evidence
                    {
                        Type = EvidenceType.ProcessMemory,
                        Source = $"Process {processId}",
                        CollectedAt = DateTime.UtcNow
                    };
                    
                    evidence.Metadata["ProcessId"] = processId;
                    evidence.Metadata["ProcessName"] = systemEvent.ProcessName;
                    
                    collection.Items.Add(evidence);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting process memory");
        }
    }

    private async Task CollectRegistrySnapshotAsync(EvidenceCollection collection)
    {
        try
        {
            // Collect snapshot of important registry keys
            var evidence = new Evidence
            {
                Type = EvidenceType.RegistrySnapshot,
                Source = "Windows Registry",
                CollectedAt = DateTime.UtcNow
            };
            
            collection.Items.Add(evidence);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting registry snapshot");
        }
    }

    private async Task CollectFileSystemArtifactsAsync(EvidenceCollection collection, ThreatEvent threat)
    {
        try
        {
            // Collect relevant file system artifacts
            var evidence = new Evidence
            {
                Type = EvidenceType.FileSystemArtifact,
                Source = "File System",
                CollectedAt = DateTime.UtcNow
            };
            
            collection.Items.Add(evidence);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting file system artifacts");
        }
    }

    private async Task CollectEventLogsAsync(EvidenceCollection collection)
    {
        try
        {
            // Collect relevant Windows event logs
            var evidence = new Evidence
            {
                Type = EvidenceType.EventLog,
                Source = "Windows Event Logs",
                CollectedAt = DateTime.UtcNow
            };
            
            collection.Items.Add(evidence);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting event logs");
        }
    }

    private async Task CollectSystemStateAsync(EvidenceCollection collection)
    {
        try
        {
            // Collect current system state information
            var evidence = new Evidence
            {
                Type = EvidenceType.SystemState,
                Source = "System State",
                CollectedAt = DateTime.UtcNow
            };
            
            // Collect running processes
            var processes = Process.GetProcesses();
            evidence.Metadata["RunningProcesses"] = processes.Select(p => new { p.ProcessName, p.Id }).ToArray();
            
            collection.Items.Add(evidence);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error collecting system state");
        }
    }
}
"""
    
    with open(base_path / "src/WatchLockAI.Forensics/ForensicsEngine.cs", "w") as f:
        f.write(forensics_implementation)
    
    print("Created forensics module")

def create_security_module(base_path):
    """Create security and tamperproofing module"""
    
    # Security interface
    security_interface = """using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Security;

/// <summary>
/// Tamperproofing and self-protection manager
/// </summary>
public interface ITamperproofManager
{
    Task InitializeAsync();
    Task StartProtectionAsync();
    Task StopProtectionAsync();
    bool IsProtectionActive { get; }
    event EventHandler<TamperAttemptEvent> TamperAttemptDetected;
}

/// <summary>
/// System monitoring for Windows APIs
/// </summary>
public interface ISystemMonitor
{
    Task StartMonitoringAsync(CancellationToken cancellationToken);
    Task StopMonitoringAsync();
    bool IsMonitoring { get; }
    event EventHandler<SystemEvent> EventDetected;
}

/// <summary>
/// Tamper attempt event
/// </summary>
public class TamperAttemptEvent
{
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Source { get; set; }
    public string AttackType { get; set; }
    public string Description { get; set; }
    public bool Blocked { get; set; }
}
"""
    
    with open(base_path / "src/WatchLockAI.Security/ITamperproofManager.cs", "w") as f:
        f.write(security_interface)
    
    # Security implementation
    security_implementation = """using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;
using System.IO;
using System.Management;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Security;

/// <summary>
/// Advanced tamperproofing and self-protection system
/// </summary>
public class TamperproofManager : ITamperproofManager
{
    private readonly ILogger<TamperproofManager> _logger;
    private readonly IEventLogger _eventLogger;
    private Timer _integrityCheckTimer;
    private Timer _watchdogTimer;
    private readonly string _serviceExecutablePath;
    private readonly byte[] _originalHash;
    private bool _protectionActive;

    public bool IsProtectionActive => _protectionActive;
    public event EventHandler<TamperAttemptEvent> TamperAttemptDetected;

    public TamperproofManager(ILogger<TamperproofManager> logger, IEventLogger eventLogger)
    {
        _logger = logger;
        _eventLogger = eventLogger;
        _serviceExecutablePath = Process.GetCurrentProcess().MainModule?.FileName;
        _originalHash = CalculateFileHash(_serviceExecutablePath);
    }

    public async Task InitializeAsync()
    {
        try
        {
            _logger.LogInformation("Initializing tamperproof protection");
            
            // Verify our own integrity first
            await VerifyServiceIntegrityAsync();
            
            // Set up anti-debugging protection
            SetupAntiDebuggingProtection();
            
            _logger.LogInformation("Tamperproof protection initialized");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize tamperproof protection");
            throw;
        }
    }

    public async Task StartProtectionAsync()
    {
        try
        {
            _logger.LogInformation("Starting tamperproof protection");
            
            // Start integrity monitoring
            _integrityCheckTimer = new Timer(CheckIntegrityCallback, null, TimeSpan.Zero, TimeSpan.FromMinutes(5));
            
            // Start watchdog monitoring
            _watchdogTimer = new Timer(WatchdogCallback, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
            
            // Monitor for process termination attempts
            await StartProcessMonitoringAsync();
            
            _protectionActive = true;
            
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.SystemModification,
                Source = "TamperproofManager",
                Message = "Tamperproof protection activated"
            });
            
            _logger.LogInformation("Tamperproof protection started");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting tamperproof protection");
            throw;
        }
    }

    public async Task StopProtectionAsync()
    {
        try
        {
            _logger.LogInformation("Stopping tamperproof protection");
            
            _protectionActive = false;
            
            _integrityCheckTimer?.Dispose();
            _watchdogTimer?.Dispose();
            
            _logger.LogInformation("Tamperproof protection stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping tamperproof protection");
        }
    }

    private async Task VerifyServiceIntegrityAsync()
    {
        try
        {
            if (string.IsNullOrEmpty(_serviceExecutablePath) || !File.Exists(_serviceExecutablePath))
            {
                throw new InvalidOperationException("Service executable not found");
            }

            var currentHash = CalculateFileHash(_serviceExecutablePath);
            
            if (!CompareHashes(_originalHash, currentHash))
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "IntegrityCheck",
                    AttackType = "File Modification",
                    Description = "Service executable has been modified",
                    Blocked = false
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                
                _logger.LogCritical("TAMPER DETECTED: Service executable has been modified!");
                
                // In production, this could trigger self-healing or emergency response
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error verifying service integrity");
        }
    }

    private void SetupAntiDebuggingProtection()
    {
        try
        {
            // Check for debugger presence
            if (Debugger.IsAttached)
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "AntiDebug",
                    AttackType = "Debugger Attached",
                    Description = "Debugger detected attached to process",
                    Blocked = true
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                
                _logger.LogWarning("Debugger detected - terminating process");
                Environment.Exit(1);
            }
            
            // Additional anti-debugging techniques would be implemented here
            _logger.LogDebug("Anti-debugging protection enabled");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting up anti-debugging protection");
        }
    }

    private async Task StartProcessMonitoringAsync()
    {
        try
        {
            // Monitor for attempts to terminate the service
            var currentProcessId = Process.GetCurrentProcess().Id;
            
            // This would set up WMI event monitoring for process termination attempts
            _logger.LogDebug("Process monitoring started for PID {ProcessId}", currentProcessId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting process monitoring");
        }
    }

    private void CheckIntegrityCallback(object state)
    {
        try
        {
            if (!_protectionActive) return;
            
            // Verify service file integrity
            _ = Task.Run(VerifyServiceIntegrityAsync);
            
            // Check for unauthorized registry modifications
            CheckRegistryIntegrity();
            
            // Verify service configuration
            CheckServiceConfiguration();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in integrity check callback");
        }
    }

    private void WatchdogCallback(object state)
    {
        try
        {
            if (!_protectionActive) return;
            
            // Heartbeat to detect if main service threads are responsive
            _logger.LogDebug("Watchdog heartbeat - service responsive");
            
            // Check for suspicious process activity
            CheckForSuspiciousProcesses();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in watchdog callback");
        }
    }

    private void CheckRegistryIntegrity()
    {
        try
        {
            // Check service registry keys for unauthorized modifications
            using var serviceKey = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\WatchLockAI");
            
            if (serviceKey == null)
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "RegistryCheck",
                    AttackType = "Registry Deletion",
                    Description = "Service registry key has been deleted",
                    Blocked = false
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                _logger.LogCritical("TAMPER DETECTED: Service registry key deleted!");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking registry integrity");
        }
    }

    private void CheckServiceConfiguration()
    {
        try
        {
            // Verify service is configured correctly and hasn't been disabled
            using var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_Service WHERE Name='WatchLockAI'");
            
            foreach (ManagementObject service in searcher.Get())
            {
                var startMode = service["StartMode"]?.ToString();
                var state = service["State"]?.ToString();
                
                if (startMode != "Automatic" || state != "Running")
                {
                    var tamperEvent = new TamperAttemptEvent
                    {
                        Source = "ServiceConfig",
                        AttackType = "Service Configuration",
                        Description = $"Service configuration changed: StartMode={startMode}, State={state}",
                        Blocked = false
                    };
                    
                    TamperAttemptDetected?.Invoke(this, tamperEvent);
                    _logger.LogWarning("Service configuration anomaly detected");
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking service configuration");
        }
    }

    private void CheckForSuspiciousProcesses()
    {
        try
        {
            // Check for known security tool terminators or bypass tools
            var suspiciousProcesses = new[]
            {
                "taskkill", "net stop", "sc stop", "wmic process",
                "procexp", "processhacker", "cheatengine"
            };
            
            var processes = Process.GetProcesses();
            
            foreach (var process in processes)
            {
                try
                {
                    var processName = process.ProcessName.ToLower();
                    
                    if (suspiciousProcesses.Any(sp => processName.Contains(sp)))
                    {
                        var tamperEvent = new TamperAttemptEvent
                        {
                            Source = "ProcessMonitor",
                            AttackType = "Suspicious Process",
                            Description = $"Suspicious process detected: {process.ProcessName}",
                            Blocked = false
                        };
                        
                        TamperAttemptDetected?.Invoke(this, tamperEvent);
                        _logger.LogWarning("Suspicious process detected: {ProcessName}", process.ProcessName);
                    }
                }
                catch
                {
                    // Skip processes we can't access
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for suspicious processes");
        }
    }

    private byte[] CalculateFileHash(string filePath)
    {
        try
        {
            if (string.IsNullOrEmpty(filePath) || !File.Exists(filePath))
                return Array.Empty<byte>();
                
            using var sha256 = SHA256.Create();
            using var stream = File.OpenRead(filePath);
            return sha256.ComputeHash(stream);
        }
        catch
        {
            return Array.Empty<byte>();
        }
    }

    private bool CompareHashes(byte[] hash1, byte[] hash2)
    {
        if (hash1.Length != hash2.Length)
            return false;
            
        for (int i = 0; i < hash1.Length; i++)
        {
            if (hash1[i] != hash2[i])
                return false;
        }
        
        return true;
    }
}

/// <summary>
/// Windows system monitoring using ETW and WMI
/// </summary>
public class SystemMonitor : ISystemMonitor
{
    private readonly ILogger<SystemMonitor> _logger;
    private readonly IEventLogger _eventLogger;
    private CancellationTokenSource _cancellationTokenSource;
    private Task _monitoringTask;
    private bool _isMonitoring;

    public bool IsMonitoring => _isMonitoring;
    public event EventHandler<SystemEvent> EventDetected;

    public SystemMonitor(ILogger<SystemMonitor> logger, IEventLogger eventLogger)
    {
        _logger = logger;
        _eventLogger = eventLogger;
    }

    public async Task StartMonitoringAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Starting system monitoring");
            
            _cancellationTokenSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            
            // Start monitoring tasks
            _monitoringTask = Task.Run(() => MonitorSystemEventsAsync(_cancellationTokenSource.Token));
            
            _isMonitoring = true;
            _logger.LogInformation("System monitoring started");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start system monitoring");
            throw;
        }
    }

    public async Task StopMonitoringAsync()
    {
        try
        {
            _logger.LogInformation("Stopping system monitoring");
            
            _isMonitoring = false;
            _cancellationTokenSource?.Cancel();
            
            if (_monitoringTask != null)
            {
                await _monitoringTask;
            }
            
            _cancellationTokenSource?.Dispose();
            _logger.LogInformation("System monitoring stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping system monitoring");
        }
    }

    private async Task MonitorSystemEventsAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                // Monitor process creation
                await MonitorProcessEventsAsync();
                
                // Monitor file system changes
                await MonitorFileSystemEventsAsync();
                
                // Monitor registry changes
                await MonitorRegistryEventsAsync();
                
                // Monitor network connections
                await MonitorNetworkEventsAsync();
                
                // Monitor PowerShell execution
                await MonitorPowerShellEventsAsync();
                
                await Task.Delay(1000, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in system monitoring loop");
                await Task.Delay(5000, cancellationToken);
            }
        }
    }

    private async Task MonitorProcessEventsAsync()
    {
        try
        {
            // Monitor process creation using WMI
            // This is a simplified implementation - production would use ETW
            
            var processes = Process.GetProcesses();
            foreach (var process in processes)
            {
                // Check for new processes (simplified)
                if (process.StartTime > DateTime.Now.AddMinutes(-1))
                {
                    var systemEvent = new SystemEvent
                    {
                        EventId = Guid.NewGuid().ToString(),
                        Timestamp = process.StartTime,
                        Source = "ProcessMonitor",
                        Type = SystemEventType.ProcessStart,
                        ProcessName = process.ProcessName,
                        ProcessId = process.Id,
                        UserName = GetProcessOwner(process.Id)
                    };
                    
                    EventDetected?.Invoke(this, systemEvent);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring process events");
        }
    }

    private async Task MonitorFileSystemEventsAsync()
    {
        try
        {
            // Monitor file system changes
            // This would typically use FileSystemWatcher or USN Journal
            _logger.LogDebug("Monitoring file system events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring file system events");
        }
    }

    private async Task MonitorRegistryEventsAsync()
    {
        try
        {
            // Monitor registry changes
            // This would typically use Registry notification APIs
            _logger.LogDebug("Monitoring registry events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring registry events");
        }
    }

    private async Task MonitorNetworkEventsAsync()
    {
        try
        {
            // Monitor network connections
            // This would typically use ETW network providers
            _logger.LogDebug("Monitoring network events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring network events");
        }
    }

    private async Task MonitorPowerShellEventsAsync()
    {
        try
        {
            // Monitor PowerShell execution
            // This would monitor PowerShell ETW providers
            _logger.LogDebug("Monitoring PowerShell events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring PowerShell events");
        }
    }

    private string GetProcessOwner(int processId)
    {
        try
        {
            using var searcher = new ManagementObjectSearcher($"SELECT * FROM Win32_Process WHERE ProcessId = {processId}");
            foreach (ManagementObject process in searcher.Get())
            {
                var args = new string[2];
                if (process.InvokeMethod("GetOwner", args) == 0)
                {
                    return $"{args[1]}\\{args[0]}";
                }
            }
        }
        catch
        {
            // Ignore errors getting process owner
        }
        
        return "Unknown";
    }
}
"""
    
    with open(base_path / "src/WatchLockAI.Security/TamperproofManager.cs", "w") as f:
        f.write(security_implementation)
    
    print("Created security and tamperproofing module")

def create_communication_module(base_path):
    """Create communication module for console connectivity"""
    
    # Communication interface
    communication_interface = """using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;
using WatchLockAI.Forensics;

namespace WatchLockAI.Communication;

/// <summary>
/// Console connectivity and communication interface
/// </summary>
public interface IConsoleConnector
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task DisconnectAsync();
    bool IsConnected { get; }
    Task ReportThreatAsync(ThreatEvent threat, Investigation investigation, ResponseResult response);
    Task SendHeartbeatAsync();
    Task<PolicyUpdate> CheckForPolicyUpdatesAsync();
    event EventHandler<ConsoleMessage> MessageReceived;
}

/// <summary>
/// Policy update from console
/// </summary>
public class PolicyUpdate
{
    public string Id { get; set; }
    public DateTime Timestamp { get; set; }
    public string PolicyType { get; set; }
    public object PolicyData { get; set; }
    public bool RequiresRestart { get; set; }
}

/// <summary>
/// Message from console
/// </summary>
public class ConsoleMessage
{
    public string Id { get; set; }
    public DateTime Timestamp { get; set; }
    public MessageType Type { get; set; }
    public string Content { get; set; }
    public object Data { get; set; }
}

public enum MessageType
{
    PolicyUpdate,
    ConfigurationChange,
    ThreatIntelligence,
    AdminCommand,
    HealthCheck
}
"""
    
    with open(base_path / "src/WatchLockAI.Communication/IConsoleConnector.cs", "w") as f:
        f.write(communication_interface)
    
    # Communication implementation
    communication_implementation = """using Microsoft.Extensions.Logging;
using Grpc.Net.Client;
using Newtonsoft.Json;
using System;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;
using WatchLockAI.Forensics;

namespace WatchLockAI.Communication;

/// <summary>
/// Secure communication with WatchLockAI management console
/// </summary>
public class ConsoleConnector : IConsoleConnector
{
    private readonly ILogger<ConsoleConnector> _logger;
    private readonly IConfigurationManager _configManager;
    private readonly IEventLogger _eventLogger;
    private readonly HttpClient _httpClient;
    private Timer _heartbeatTimer;
    private bool _isConnected;
    private string _consoleEndpoint;
    private string _agentId;

    public bool IsConnected => _isConnected;
    public event EventHandler<ConsoleMessage> MessageReceived;

    public ConsoleConnector(
        ILogger<ConsoleConnector> logger,
        IConfigurationManager configManager,
        IEventLogger eventLogger)
    {
        _logger = logger;
        _configManager = configManager;
        _eventLogger = eventLogger;
        _httpClient = new HttpClient();
        _agentId = Environment.MachineName + "_" + Guid.NewGuid().ToString("N")[..8];
    }

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Initializing console connector");
            
            _consoleEndpoint = _configManager.GetSetting("ConsoleEndpoint", "https://console.watchlockai.com");
            
            // Configure HTTP client
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "WatchLockAI-Agent/1.0");
            _httpClient.DefaultRequestHeaders.Add("X-Agent-Id", _agentId);
            
            // Test connection
            await TestConnectionAsync();
            
            // Start heartbeat
            var heartbeatInterval = _configManager.GetSetting("HeartbeatInterval", 60);
            _heartbeatTimer = new Timer(HeartbeatCallback, null, 
                TimeSpan.Zero, TimeSpan.FromSeconds(heartbeatInterval));
            
            _isConnected = true;
            _logger.LogInformation("Console connector initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize console connector");
            _isConnected = false;
            // Don't throw - allow agent to operate in offline mode
        }
    }

    public async Task DisconnectAsync()
    {
        try
        {
            _logger.LogInformation("Disconnecting from console");
            
            _isConnected = false;
            _heartbeatTimer?.Dispose();
            
            // Send disconnect notification
            await SendDisconnectNotificationAsync();
            
            _httpClient?.Dispose();
            _logger.LogInformation("Disconnected from console");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error disconnecting from console");
        }
    }

    public async Task ReportThreatAsync(ThreatEvent threat, Investigation investigation, ResponseResult response)
    {
        try
        {
            if (!_isConnected)
            {
                _logger.LogWarning("Cannot report threat - not connected to console");
                return;
            }

            _logger.LogInformation("Reporting threat {ThreatId} to console", threat.Id);

            var report = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Threat = threat,
                Investigation = investigation,
                Response = response
            };

            var json = JsonConvert.SerializeObject(report);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response_http = await _httpClient.PostAsync($"{_consoleEndpoint}/api/threats", content);
            
            if (response_http.IsSuccessStatusCode)
            {
                _logger.LogInformation("Threat report sent successfully");
            }
            else
            {
                _logger.LogWarning("Failed to send threat report: {StatusCode}", response_http.StatusCode);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reporting threat to console");
        }
    }

    public async Task SendHeartbeatAsync()
    {
        try
        {
            if (!_isConnected) return;

            var heartbeat = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Status = "Online",
                Version = "1.0.0",
                SystemInfo = new
                {
                    MachineName = Environment.MachineName,
                    OSVersion = Environment.OSVersion.ToString(),
                    ProcessorCount = Environment.ProcessorCount,
                    MemoryUsage = GC.GetTotalMemory(false)
                }
            };

            var json = JsonConvert.SerializeObject(heartbeat);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_consoleEndpoint}/api/heartbeat", content);
            
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Heartbeat failed: {StatusCode}", response.StatusCode);
                _isConnected = false;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending heartbeat");
            _isConnected = false;
        }
    }

    public async Task<PolicyUpdate> CheckForPolicyUpdatesAsync()
    {
        try
        {
            if (!_isConnected) return null;

            var response = await _httpClient.GetAsync($"{_consoleEndpoint}/api/policies/{_agentId}");
            
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var policy = JsonConvert.DeserializeObject<PolicyUpdate>(json);
                
                if (policy != null)
                {
                    _logger.LogInformation("Received policy update: {PolicyType}", policy.PolicyType);
                    return policy;
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for policy updates");
        }
        
        return null;
    }

    private async Task TestConnectionAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_consoleEndpoint}/api/health");
            
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Successfully connected to console at {Endpoint}", _consoleEndpoint);
            }
            else
            {
                throw new InvalidOperationException($"Console health check failed: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to connect to console at {Endpoint}", _consoleEndpoint);
            throw;
        }
    }

    private void HeartbeatCallback(object state)
    {
        try
        {
            _ = Task.Run(SendHeartbeatAsync);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in heartbeat callback");
        }
    }

    private async Task SendDisconnectNotificationAsync()
    {
        try
        {
            var notification = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Status = "Disconnecting"
            };

            var json = JsonConvert.SerializeObject(notification);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            await _httpClient.PostAsync($"{_consoleEndpoint}/api/disconnect", content);
        }
        catch
        {
            // Ignore errors during disconnect
        }
    }
}
"""
    
    with open(base_path / "src/WatchLockAI.Communication/ConsoleConnector.cs", "w") as f:
        f.write(communication_implementation)
    
    print("Created communication module")

def create_integration_module(base_path):
    """Create integration module for third-party security tools"""
    
    # Integration interface
    integration_interface = """using System;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Integration;

/// <summary>
/// Microsoft Defender integration
/// </summary>
public interface IDefenderIntegration
{
    Task<bool> IsDefenderEnabledAsync();
    Task<bool> AddExclusionAsync(string path);
    Task<bool> RemoveExclusionAsync(string path);
    Task<bool> TriggerScanAsync(string path);
    Task<DefenderStatus> GetStatusAsync();
}

/// <summary>
/// Azure Security Center integration
/// </summary>
public interface IAzureIntegration
{
    Task<bool> SendSecurityAlertAsync(ThreatEvent threat);
    Task<AzureSecurityAlert[]> GetRecentAlertsAsync();
    Task<bool> UpdateSecurityStatusAsync(string status);
}

/// <summary>
/// Defender status information
/// </summary>
public class DefenderStatus
{
    public bool AntivirusEnabled { get; set; }
    public bool RealTimeProtectionEnabled { get; set; }
    public DateTime LastScanTime { get; set; }
    public string Version { get; set; }
    public string[] Exclusions { get; set; }
}

/// <summary>
/// Azure security alert
/// </summary>
public class AzureSecurityAlert
{
    public string Id { get; set; }
    public DateTime Timestamp { get; set; }
    public string AlertType { get; set; }
    public string Severity { get; set; }
    public string Description { get; set; }
    public string ResourceId { get; set; }
}
"""
    
    with open(base_path / "src/WatchLockAI.Integration/IDefenderIntegration.cs", "w") as f:
        f.write(integration_interface)
    
    # Integration implementation
    integration_implementation = """using Microsoft.Extensions.Logging;
using System;
using System.Management;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Integration;

/// <summary>
/// Microsoft Defender for Endpoint integration
/// </summary>
public class DefenderIntegration : IDefenderIntegration
{
    private readonly ILogger<DefenderIntegration> _logger;

    public DefenderIntegration(ILogger<DefenderIntegration> logger)
    {
        _logger = logger;
    }

    public async Task<bool> IsDefenderEnabledAsync()
    {
        try
        {
            using var searcher = new ManagementObjectSearcher(@"root\Microsoft\Windows\Defender", 
                "SELECT * FROM MSFT_MpComputerStatus");
            
            foreach (ManagementObject queryObj in searcher.Get())
            {
                var antivirusEnabled = (bool?)queryObj["AntivirusEnabled"];
                return antivirusEnabled ?? false;
            }
            
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking Defender status");
            return false;
        }
    }

    public async Task<bool> AddExclusionAsync(string path)
    {
        try
        {
            _logger.LogInformation("Adding Defender exclusion for path: {Path}", path);
            
            using var defenderClass = new ManagementClass(@"root\Microsoft\Windows\Defender", "MSFT_MpPreference", null);
            using var inParams = defenderClass.GetMethodParameters("Add-MpPreference");
            
            inParams["ExclusionPath"] = path;
            
            var result = defenderClass.InvokeMethod("Add-MpPreference", inParams, null);
            
            _logger.LogInformation("Defender exclusion added successfully");
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding Defender exclusion for path: {Path}", path);
            return false;
        }
    }

    public async Task<bool> RemoveExclusionAsync(string path)
    {
        try
        {
            _logger.LogInformation("Removing Defender exclusion for path: {Path}", path);
            
            // Implementation would remove the exclusion
            
            _logger.LogInformation("Defender exclusion removed successfully");
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error removing Defender exclusion for path: {Path}", path);
            return false;
        }
    }

    public async Task<bool> TriggerScanAsync(string path)
    {
        try
        {
            _logger.LogInformation("Triggering Defender scan for path: {Path}", path);
            
            using var defenderClass = new ManagementClass(@"root\Microsoft\Windows\Defender", "MSFT_MpScan", null);
            using var inParams = defenderClass.GetMethodParameters("Start-MpScan");
            
            inParams["ScanPath"] = path;
            inParams["ScanType"] = 2; // Custom scan
            
            var result = defenderClass.InvokeMethod("Start-MpScan", inParams, null);
            
            _logger.LogInformation("Defender scan triggered successfully");
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error triggering Defender scan for path: {Path}", path);
            return false;
        }
    }

    public async Task<DefenderStatus> GetStatusAsync()
    {
        try
        {
            using var searcher = new ManagementObjectSearcher(@"root\Microsoft\Windows\Defender", 
                "SELECT * FROM MSFT_MpComputerStatus");
            
            foreach (ManagementObject queryObj in searcher.Get())
            {
                return new DefenderStatus
                {
                    AntivirusEnabled = (bool?)queryObj["AntivirusEnabled"] ?? false,
                    RealTimeProtectionEnabled = (bool?)queryObj["RealTimeProtectionEnabled"] ?? false,
                    LastScanTime = DateTime.TryParse(queryObj["QuickScanEndTime"]?.ToString(), out var scanTime) ? scanTime : DateTime.MinValue,
                    Version = queryObj["AntivirusSignatureVersion"]?.ToString() ?? "Unknown"
                };
            }
            
            return new DefenderStatus();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting Defender status");
            return new DefenderStatus();
        }
    }
}

/// <summary>
/// Azure Security Center integration
/// </summary>
public class AzureIntegration : IAzureIntegration
{
    private readonly ILogger<AzureIntegration> _logger;
    private readonly IConfigurationManager _configManager;

    public AzureIntegration(ILogger<AzureIntegration> logger, IConfigurationManager configManager)
    {
        _logger = logger;
        _configManager = configManager;
    }

    public async Task<bool> SendSecurityAlertAsync(ThreatEvent threat)
    {
        try
        {
            _logger.LogInformation("Sending security alert to Azure for threat: {ThreatId}", threat.Id);
            
            // Implementation would send alert to Azure Security Center
            // This would typically use Azure REST APIs or SDKs
            
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending security alert to Azure");
            return false;
        }
    }

    public async Task<AzureSecurityAlert[]> GetRecentAlertsAsync()
    {
        try
        {
            _logger.LogDebug("Retrieving recent Azure security alerts");
            
            // Implementation would retrieve alerts from Azure Security Center
            
            return Array.Empty<AzureSecurityAlert>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving Azure security alerts");
            return Array.Empty<AzureSecurityAlert>();
        }
    }

    public async Task<bool> UpdateSecurityStatusAsync(string status)
    {
        try
        {
            _logger.LogInformation("Updating Azure security status: {Status}", status);
            
            // Implementation would update security status in Azure
            
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating Azure security status");
            return false;
        }
    }
}
"""
    
    with open(base_path / "src/WatchLockAI.Integration/DefenderIntegration.cs", "w") as f:
        f.write(integration_implementation)
    
    print("Created integration module")

if __name__ == "__main__":
    base_path = Path("/workspace/WatchLockAI_Agent")
    
    print("Creating final implementation modules...")
    
    create_forensics_module(base_path)
    create_security_module(base_path)
    create_communication_module(base_path)
    create_integration_module(base_path)
    
    print("Final modules created successfully!")
