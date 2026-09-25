using System;
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
