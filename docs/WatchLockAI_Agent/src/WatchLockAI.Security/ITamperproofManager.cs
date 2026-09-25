using System;
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
