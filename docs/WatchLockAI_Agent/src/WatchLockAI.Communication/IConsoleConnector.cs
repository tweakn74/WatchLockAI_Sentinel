using System;
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
