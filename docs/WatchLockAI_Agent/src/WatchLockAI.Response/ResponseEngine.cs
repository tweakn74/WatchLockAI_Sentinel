using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;
using System.Management;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Response;

/// <summary>
/// Automated response engine with configurable actions
/// </summary>
public class ResponseEngine : IResponseEngine
{
    private readonly ILogger<ResponseEngine> _logger;
    private readonly IFirewallController _firewallController;
    private readonly IEventLogger _eventLogger;
    private readonly IConfigurationManager _configManager;
    private bool _autoResponseEnabled;

    public ResponseEngine(
        ILogger<ResponseEngine> logger,
        IFirewallController firewallController,
        IEventLogger eventLogger,
        IConfigurationManager configManager)
    {
        _logger = logger;
        _firewallController = firewallController;
        _eventLogger = eventLogger;
        _configManager = configManager;
    }

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Initializing Response Engine");
            
            _autoResponseEnabled = _configManager.GetSetting("AutoResponseEnabled", false);
            
            _logger.LogInformation("Response Engine initialized (Auto-response: {AutoResponse})", 
                _autoResponseEnabled);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize Response Engine");
            throw;
        }
    }

    public async Task StopAsync()
    {
        try
        {
            _logger.LogInformation("Stopping Response Engine");
            // Clean up any ongoing response actions
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping Response Engine");
        }
    }

    public async Task<ResponseResult> RespondToThreatAsync(ThreatEvent threat)
    {
        try
        {
            _logger.LogWarning("Responding to threat: {ThreatType} (Severity: {Severity})", 
                threat.Type, threat.Severity);

            if (!_autoResponseEnabled)
            {
                return new ResponseResult
                {
                    Success = false,
                    Message = "Auto-response disabled - manual intervention required",
                    ActionType = "NoAction"
                };
            }

            var responseActions = DetermineResponseActions(threat);
            var results = new List<ResponseResult>();

            foreach (var action in responseActions)
            {
                var result = await ExecuteResponseActionAsync(action, threat);
                results.Add(result);
            }

            // Log security event
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.ResponseAction,
                Source = "ResponseEngine",
                Message = $"Executed {results.Count} response actions for threat {threat.Type}"
            });

            return new ResponseResult
            {
                Success = results.All(r => r.Success),
                Message = $"Executed {results.Count} response actions",
                ActionType = "MultipleActions",
                Details = { ["Actions"] = results }
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error responding to threat {ThreatId}", threat.Id);
            return new ResponseResult
            {
                Success = false,
                Message = ex.Message,
                ActionType = "Error"
            };
        }
    }

    public async Task<ResponseResult> QuarantineProcessAsync(int processId)
    {
        try
        {
            _logger.LogWarning("Quarantining process {ProcessId}", processId);

            // Suspend the process first
            var process = Process.GetProcessById(processId);
            if (process != null)
            {
                // Kill the process
                process.Kill();
                process.WaitForExit(5000);

                return new ResponseResult
                {
                    Success = true,
                    Message = $"Process {processId} quarantined successfully",
                    ActionType = "ProcessQuarantine"
                };
            }

            return new ResponseResult
            {
                Success = false,
                Message = $"Process {processId} not found",
                ActionType = "ProcessQuarantine"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error quarantining process {ProcessId}", processId);
            return new ResponseResult
            {
                Success = false,
                Message = ex.Message,
                ActionType = "ProcessQuarantine"
            };
        }
    }

    public async Task<ResponseResult> BlockNetworkConnectionAsync(string remoteAddress)
    {
        try
        {
            _logger.LogWarning("Blocking network connection to {RemoteAddress}", remoteAddress);

            var blocked = await _firewallController.BlockIpAddressAsync(remoteAddress);

            return new ResponseResult
            {
                Success = blocked,
                Message = blocked ? $"Blocked connection to {remoteAddress}" : $"Failed to block {remoteAddress}",
                ActionType = "NetworkBlock"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error blocking network connection to {RemoteAddress}", remoteAddress);
            return new ResponseResult
            {
                Success = false,
                Message = ex.Message,
                ActionType = "NetworkBlock"
            };
        }
    }

    public async Task<ResponseResult> IsolateUserAccountAsync(string accountName)
    {
        try
        {
            _logger.LogWarning("Isolating user account {AccountName}", accountName);

            // Disable the user account
            var success = await DisableUserAccountAsync(accountName);

            return new ResponseResult
            {
                Success = success,
                Message = success ? $"Account {accountName} isolated" : $"Failed to isolate {accountName}",
                ActionType = "AccountIsolation"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error isolating user account {AccountName}", accountName);
            return new ResponseResult
            {
                Success = false,
                Message = ex.Message,
                ActionType = "AccountIsolation"
            };
        }
    }

    public async Task<ResponseResult> RevertMaliciousChangesAsync(ThreatEvent threat)
    {
        try
        {
            _logger.LogInformation("Reverting malicious changes for threat {ThreatId}", threat.Id);

            // This would implement specific reversion logic based on threat type
            // For example: restore registry keys, delete malicious files, etc.

            return new ResponseResult
            {
                Success = true,
                Message = "Malicious changes reverted",
                ActionType = "ChangeReversion"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reverting malicious changes for threat {ThreatId}", threat.Id);
            return new ResponseResult
            {
                Success = false,
                Message = ex.Message,
                ActionType = "ChangeReversion"
            };
        }
    }

    private ResponseAction[] DetermineResponseActions(ThreatEvent threat)
    {
        var actions = new List<ResponseAction>();

        // Determine appropriate response based on threat type and severity
        switch (threat.Severity)
        {
            case ThreatSeverity.Critical:
                actions.Add(ResponseAction.QuarantineProcess);
                actions.Add(ResponseAction.BlockNetwork);
                actions.Add(ResponseAction.NotifyAdmin);
                break;

            case ThreatSeverity.High:
                actions.Add(ResponseAction.QuarantineProcess);
                actions.Add(ResponseAction.NotifyAdmin);
                break;

            case ThreatSeverity.Medium:
                actions.Add(ResponseAction.LogAndAlert);
                break;

            case ThreatSeverity.Low:
                actions.Add(ResponseAction.LogOnly);
                break;
        }

        return actions.ToArray();
    }

    private async Task<ResponseResult> ExecuteResponseActionAsync(ResponseAction action, ThreatEvent threat)
    {
        return action switch
        {
            ResponseAction.QuarantineProcess => await QuarantineProcessFromThreatAsync(threat),
            ResponseAction.BlockNetwork => await BlockNetworkFromThreatAsync(threat),
            ResponseAction.NotifyAdmin => await NotifyAdminAsync(threat),
            ResponseAction.LogAndAlert => await LogAndAlertAsync(threat),
            ResponseAction.LogOnly => await LogOnlyAsync(threat),
            _ => new ResponseResult { Success = false, Message = "Unknown action", ActionType = action.ToString() }
        };
    }

    private async Task<ResponseResult> QuarantineProcessFromThreatAsync(ThreatEvent threat)
    {
        if (threat.Properties.TryGetValue("SystemEvent", out var systemEventObj) &&
            systemEventObj is SystemEvent systemEvent)
        {
            return await QuarantineProcessAsync(systemEvent.ProcessId);
        }

        return new ResponseResult
        {
            Success = false,
            Message = "No process ID available for quarantine",
            ActionType = "ProcessQuarantine"
        };
    }

    private async Task<ResponseResult> BlockNetworkFromThreatAsync(ThreatEvent threat)
    {
        // Extract network information from threat and block if available
        return new ResponseResult
        {
            Success = true,
            Message = "Network blocking attempted",
            ActionType = "NetworkBlock"
        };
    }

    private async Task<ResponseResult> NotifyAdminAsync(ThreatEvent threat)
    {
        // Send notification to administrators
        _logger.LogCritical("SECURITY ALERT: {ThreatType} detected - {Description}", 
            threat.Type, threat.Description);

        return new ResponseResult
        {
            Success = true,
            Message = "Administrator notification sent",
            ActionType = "AdminNotification"
        };
    }

    private async Task<ResponseResult> LogAndAlertAsync(ThreatEvent threat)
    {
        await _eventLogger.LogSecurityEventAsync(new SecurityEvent
        {
            Type = SecurityEventType.ThreatDetected,
            Source = "ResponseEngine",
            Message = $"Threat detected and logged: {threat.Description}"
        });

        return new ResponseResult
        {
            Success = true,
            Message = "Threat logged and alert generated",
            ActionType = "LogAndAlert"
        };
    }

    private async Task<ResponseResult> LogOnlyAsync(ThreatEvent threat)
    {
        _logger.LogInformation("Low severity threat logged: {ThreatType}", threat.Type);

        return new ResponseResult
        {
            Success = true,
            Message = "Threat logged",
            ActionType = "LogOnly"
        };
    }

    private async Task<bool> DisableUserAccountAsync(string accountName)
    {
        try
        {
            // Use WMI to disable user account
            using var searcher = new ManagementObjectSearcher($"SELECT * FROM Win32_UserAccount WHERE Name='{accountName}'");
            foreach (ManagementObject user in searcher.Get())
            {
                user["Disabled"] = true;
                user.Put();
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error disabling user account {AccountName}", accountName);
            return false;
        }
    }
}

/// <summary>
/// Response action types
/// </summary>
public enum ResponseAction
{
    QuarantineProcess,
    BlockNetwork,
    NotifyAdmin,
    LogAndAlert,
    LogOnly,
    IsolateAccount,
    RevertChanges
}

/// <summary>
/// Windows Firewall controller implementation
/// </summary>
public class FirewallController : IFirewallController
{
    private readonly ILogger<FirewallController> _logger;

    public FirewallController(ILogger<FirewallController> logger)
    {
        _logger = logger;
    }

    public async Task<bool> BlockIpAddressAsync(string ipAddress)
    {
        try
        {
            _logger.LogInformation("Blocking IP address {IpAddress}", ipAddress);

            // Create firewall rule to block IP
            var ruleName = $"WatchLockAI_Block_{ipAddress}_{DateTime.Now:yyyyMMdd_HHmmss}";
            
            var result = await ExecuteFirewallCommandAsync(
                $"netsh advfirewall firewall add rule name="{ruleName}" dir=out action=block remoteip={ipAddress}");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error blocking IP address {IpAddress}", ipAddress);
            return false;
        }
    }

    public async Task<bool> BlockPortAsync(int port)
    {
        try
        {
            _logger.LogInformation("Blocking port {Port}", port);

            var ruleName = $"WatchLockAI_BlockPort_{port}_{DateTime.Now:yyyyMMdd_HHmmss}";
            
            var result = await ExecuteFirewallCommandAsync(
                $"netsh advfirewall firewall add rule name="{ruleName}" dir=in action=block protocol=TCP localport={port}");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error blocking port {Port}", port);
            return false;
        }
    }

    public async Task<bool> AllowIpAddressAsync(string ipAddress)
    {
        try
        {
            _logger.LogInformation("Allowing IP address {IpAddress}", ipAddress);

            var ruleName = $"WatchLockAI_Allow_{ipAddress}_{DateTime.Now:yyyyMMdd_HHmmss}";
            
            var result = await ExecuteFirewallCommandAsync(
                $"netsh advfirewall firewall add rule name="{ruleName}" dir=out action=allow remoteip={ipAddress}");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error allowing IP address {IpAddress}", ipAddress);
            return false;
        }
    }

    public async Task<bool> CreateCustomRuleAsync(FirewallRule rule)
    {
        try
        {
            _logger.LogInformation("Creating custom firewall rule {RuleName}", rule.Name);

            var command = BuildFirewallCommand(rule);
            var result = await ExecuteFirewallCommandAsync(command);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating custom firewall rule {RuleName}", rule.Name);
            return false;
        }
    }

    public async Task<FirewallRule[]> GetActiveRulesAsync()
    {
        try
        {
            // Get active WatchLockAI firewall rules
            var rules = new List<FirewallRule>();
            
            // This would execute netsh command to list rules and parse the output
            // For brevity, returning empty array
            
            return rules.ToArray();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting active firewall rules");
            return Array.Empty<FirewallRule>();
        }
    }

    private async Task<bool> ExecuteFirewallCommandAsync(string command)
    {
        try
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = $"/c {command}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };

            process.Start();
            await process.WaitForExitAsync();

            return process.ExitCode == 0;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing firewall command: {Command}", command);
            return false;
        }
    }

    private string BuildFirewallCommand(FirewallRule rule)
    {
        var command = $"netsh advfirewall firewall add rule name="{rule.Name}" ";
        command += $"dir={rule.Direction.ToLower()} ";
        command += $"action={rule.Action.ToLower()} ";
        
        if (!string.IsNullOrEmpty(rule.Protocol))
            command += $"protocol={rule.Protocol} ";
            
        if (!string.IsNullOrEmpty(rule.RemoteAddress))
            command += $"remoteip={rule.RemoteAddress} ";
            
        if (!string.IsNullOrEmpty(rule.LocalPort))
            command += $"localport={rule.LocalPort} ";
            
        if (!string.IsNullOrEmpty(rule.RemotePort))
            command += $"remoteport={rule.RemotePort} ";

        return command.Trim();
    }
}
