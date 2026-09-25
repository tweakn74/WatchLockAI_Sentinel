using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Response;

/// <summary>
/// Automated threat response and containment engine
/// </summary>
public interface IResponseEngine
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task StopAsync();
    Task<ResponseResult> RespondToThreatAsync(ThreatEvent threat);
    Task<ResponseResult> QuarantineProcessAsync(int processId);
    Task<ResponseResult> BlockNetworkConnectionAsync(string remoteAddress);
    Task<ResponseResult> IsolateUserAccountAsync(string accountName);
    Task<ResponseResult> RevertMaliciousChangesAsync(ThreatEvent threat);
}

/// <summary>
/// Firewall control for network-based responses
/// </summary>
public interface IFirewallController
{
    Task<bool> BlockIpAddressAsync(string ipAddress);
    Task<bool> BlockPortAsync(int port);
    Task<bool> AllowIpAddressAsync(string ipAddress);
    Task<bool> CreateCustomRuleAsync(FirewallRule rule);
    Task<FirewallRule[]> GetActiveRulesAsync();
}

/// <summary>
/// Firewall rule definition
/// </summary>
public class FirewallRule
{
    public string Name { get; set; }
    public string Direction { get; set; } // Inbound/Outbound
    public string Action { get; set; } // Allow/Block
    public string Protocol { get; set; } // TCP/UDP/Any
    public string LocalAddress { get; set; }
    public string RemoteAddress { get; set; }
    public string LocalPort { get; set; }
    public string RemotePort { get; set; }
    public bool Enabled { get; set; }
    public DateTime CreatedAt { get; set; }
}
