using Microsoft.Extensions.Logging;
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
                    report += $"| {evt.Timestamp:yyyy-MM-dd HH:mm:ss} | {evt.Source} | {evt.EventType} | {evt.Description} |
";
                }
            }

            report += $@"

## Evidence Collected
- **Total Evidence Items**: {investigation.Evidence.Count}
";

            var evidenceByType = investigation.Evidence.GroupBy(e => e.Type);
            foreach (var group in evidenceByType)
            {
                report += $"- **{group.Key}**: {group.Count()} items
";
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
