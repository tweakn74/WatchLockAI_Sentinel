using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Core;

/// <summary>
/// Main orchestration engine for WatchLockAI
/// </summary>
public interface ICoreEngine
{
    Task StartAsync(CancellationToken cancellationToken);
    Task StopAsync();
    bool IsRunning { get; }
    event EventHandler<ThreatEvent> ThreatDetected;
    event EventHandler<SystemEvent> SystemEventOccurred;
}
