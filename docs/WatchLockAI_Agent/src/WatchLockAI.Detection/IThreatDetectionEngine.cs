using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Detection;

/// <summary>
/// MITRE ATT&CK aware threat detection engine
/// </summary>
public interface IThreatDetectionEngine
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task StopAsync();
    event EventHandler<ThreatEvent> ThreatDetected;
    Task<ThreatEvent> AnalyzeThreatAsync(SystemEvent systemEvent);
    Task UpdateThreatIntelligenceAsync();
}

/// <summary>
/// Account monitoring and baseline management
/// </summary>
public interface IAccountSentinel
{
    Task StartMonitoringAsync(CancellationToken cancellationToken);
    Task StopMonitoringAsync();
    Task<bool> IsAccountAnomalousAsync(string accountName);
    Task UpdateAccountBaselineAsync(string accountName);
    event EventHandler<AccountEvent> AccountAnomalyDetected;
}

/// <summary>
/// Account-related events
/// </summary>
public class AccountEvent
{
    public string AccountName { get; set; }
    public string EventType { get; set; }
    public DateTime Timestamp { get; set; }
    public string Description { get; set; }
    public AccountAnomalyType AnomalyType { get; set; }
}

public enum AccountAnomalyType
{
    NewAccount,
    UnusualLogonTime,
    UnusualLogonLocation,
    PrivilegeEscalation,
    SuspiciousActivity,
    AccountMisuse
}
