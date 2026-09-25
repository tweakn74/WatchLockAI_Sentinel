using System;
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
