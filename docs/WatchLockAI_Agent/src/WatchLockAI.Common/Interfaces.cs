using System;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace WatchLockAI.Common;

/// <summary>
/// Core configuration management interface
/// </summary>
public interface IConfigurationManager
{
    T GetSetting<T>(string key, T defaultValue = default);
    void SetSetting<T>(string key, T value);
    Task SaveAsync();
    Task LoadAsync();
}

/// <summary>
/// Event logging interface for system-wide logging
/// </summary>
public interface IEventLogger
{
    Task LogInformationAsync(string message, object data = null);
    Task LogWarningAsync(string message, object data = null);
    Task LogErrorAsync(string message, Exception exception = null, object data = null);
    Task LogSecurityEventAsync(SecurityEvent securityEvent);
}

/// <summary>
/// System monitoring interface for Windows APIs
/// </summary>
public interface ISystemMonitor
{
    Task StartMonitoringAsync(CancellationToken cancellationToken);
    Task StopMonitoringAsync();
    event EventHandler<SystemEvent> EventDetected;
    bool IsMonitoring { get; }
}

/// <summary>
/// Base threat event structure
/// </summary>
public class ThreatEvent
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Source { get; set; }
    public string Type { get; set; }
    public ThreatSeverity Severity { get; set; }
    public string Description { get; set; }
    public Dictionary<string, object> Properties { get; set; } = new();
    public string MitreAttackTechnique { get; set; }
    public string KillChainPhase { get; set; }
}

/// <summary>
/// Security event for audit logging
/// </summary>
public class SecurityEvent
{
    public string EventId { get; set; } = Guid.NewGuid().ToString();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Source { get; set; }
    public SecurityEventType Type { get; set; }
    public string Message { get; set; }
    public string UserId { get; set; }
    public string ProcessName { get; set; }
    public Dictionary<string, object> AdditionalData { get; set; } = new();
}

/// <summary>
/// System event from Windows monitoring
/// </summary>
public class SystemEvent
{
    public string EventId { get; set; }
    public DateTime Timestamp { get; set; }
    public string Source { get; set; }
    public SystemEventType Type { get; set; }
    public string ProcessName { get; set; }
    public int ProcessId { get; set; }
    public string CommandLine { get; set; }
    public string UserName { get; set; }
    public Dictionary<string, object> Properties { get; set; } = new();
}

/// <summary>
/// Threat severity levels
/// </summary>
public enum ThreatSeverity
{
    Low,
    Medium,
    High,
    Critical
}

/// <summary>
/// Security event types
/// </summary>
public enum SecurityEventType
{
    Authentication,
    Authorization,
    ThreatDetected,
    ResponseAction,
    SystemModification,
    NetworkActivity,
    FileAccess,
    RegistryAccess,
    ProcessExecution
}

/// <summary>
/// System event types
/// </summary>
public enum SystemEventType
{
    ProcessStart,
    ProcessStop,
    FileCreated,
    FileModified,
    FileDeleted,
    RegistryKeyCreated,
    RegistryKeyModified,
    RegistryKeyDeleted,
    NetworkConnection,
    PowerShellExecution,
    WmiQuery,
    ServiceInstalled,
    ServiceStarted,
    ServiceStopped
}

/// <summary>
/// Response action results
/// </summary>
public class ResponseResult
{
    public bool Success { get; set; }
    public string Message { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string ActionType { get; set; }
    public Dictionary<string, object> Details { get; set; } = new();
}

/// <summary>
/// Behavioral baseline data
/// </summary>
public class BehavioralBaseline
{
    public string EntityId { get; set; }
    public string EntityType { get; set; } // User, Process, System
    public DateTime CreatedAt { get; set; }
    public DateTime LastUpdated { get; set; }
    public Dictionary<string, object> Patterns { get; set; } = new();
    public double DeviationThreshold { get; set; } = 0.8;
}
