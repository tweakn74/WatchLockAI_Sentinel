using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;
using System.IO;
using System.Management;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Security;

/// <summary>
/// Advanced tamperproofing and self-protection system
/// </summary>
public class TamperproofManager : ITamperproofManager
{
    private readonly ILogger<TamperproofManager> _logger;
    private readonly IEventLogger _eventLogger;
    private Timer _integrityCheckTimer;
    private Timer _watchdogTimer;
    private readonly string _serviceExecutablePath;
    private readonly byte[] _originalHash;
    private bool _protectionActive;

    public bool IsProtectionActive => _protectionActive;
    public event EventHandler<TamperAttemptEvent> TamperAttemptDetected;

    public TamperproofManager(ILogger<TamperproofManager> logger, IEventLogger eventLogger)
    {
        _logger = logger;
        _eventLogger = eventLogger;
        _serviceExecutablePath = Process.GetCurrentProcess().MainModule?.FileName;
        _originalHash = CalculateFileHash(_serviceExecutablePath);
    }

    public async Task InitializeAsync()
    {
        try
        {
            _logger.LogInformation("Initializing tamperproof protection");
            
            // Verify our own integrity first
            await VerifyServiceIntegrityAsync();
            
            // Set up anti-debugging protection
            SetupAntiDebuggingProtection();
            
            _logger.LogInformation("Tamperproof protection initialized");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize tamperproof protection");
            throw;
        }
    }

    public async Task StartProtectionAsync()
    {
        try
        {
            _logger.LogInformation("Starting tamperproof protection");
            
            // Start integrity monitoring
            _integrityCheckTimer = new Timer(CheckIntegrityCallback, null, TimeSpan.Zero, TimeSpan.FromMinutes(5));
            
            // Start watchdog monitoring
            _watchdogTimer = new Timer(WatchdogCallback, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
            
            // Monitor for process termination attempts
            await StartProcessMonitoringAsync();
            
            _protectionActive = true;
            
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.SystemModification,
                Source = "TamperproofManager",
                Message = "Tamperproof protection activated"
            });
            
            _logger.LogInformation("Tamperproof protection started");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting tamperproof protection");
            throw;
        }
    }

    public async Task StopProtectionAsync()
    {
        try
        {
            _logger.LogInformation("Stopping tamperproof protection");
            
            _protectionActive = false;
            
            _integrityCheckTimer?.Dispose();
            _watchdogTimer?.Dispose();
            
            _logger.LogInformation("Tamperproof protection stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping tamperproof protection");
        }
    }

    private async Task VerifyServiceIntegrityAsync()
    {
        try
        {
            if (string.IsNullOrEmpty(_serviceExecutablePath) || !File.Exists(_serviceExecutablePath))
            {
                throw new InvalidOperationException("Service executable not found");
            }

            var currentHash = CalculateFileHash(_serviceExecutablePath);
            
            if (!CompareHashes(_originalHash, currentHash))
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "IntegrityCheck",
                    AttackType = "File Modification",
                    Description = "Service executable has been modified",
                    Blocked = false
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                
                _logger.LogCritical("TAMPER DETECTED: Service executable has been modified!");
                
                // In production, this could trigger self-healing or emergency response
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error verifying service integrity");
        }
    }

    private void SetupAntiDebuggingProtection()
    {
        try
        {
            // Check for debugger presence
            if (Debugger.IsAttached)
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "AntiDebug",
                    AttackType = "Debugger Attached",
                    Description = "Debugger detected attached to process",
                    Blocked = true
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                
                _logger.LogWarning("Debugger detected - terminating process");
                Environment.Exit(1);
            }
            
            // Additional anti-debugging techniques would be implemented here
            _logger.LogDebug("Anti-debugging protection enabled");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting up anti-debugging protection");
        }
    }

    private async Task StartProcessMonitoringAsync()
    {
        try
        {
            // Monitor for attempts to terminate the service
            var currentProcessId = Process.GetCurrentProcess().Id;
            
            // This would set up WMI event monitoring for process termination attempts
            _logger.LogDebug("Process monitoring started for PID {ProcessId}", currentProcessId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting process monitoring");
        }
    }

    private void CheckIntegrityCallback(object state)
    {
        try
        {
            if (!_protectionActive) return;
            
            // Verify service file integrity
            _ = Task.Run(VerifyServiceIntegrityAsync);
            
            // Check for unauthorized registry modifications
            CheckRegistryIntegrity();
            
            // Verify service configuration
            CheckServiceConfiguration();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in integrity check callback");
        }
    }

    private void WatchdogCallback(object state)
    {
        try
        {
            if (!_protectionActive) return;
            
            // Heartbeat to detect if main service threads are responsive
            _logger.LogDebug("Watchdog heartbeat - service responsive");
            
            // Check for suspicious process activity
            CheckForSuspiciousProcesses();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in watchdog callback");
        }
    }

    private void CheckRegistryIntegrity()
    {
        try
        {
            // Check service registry keys for unauthorized modifications
            using var serviceKey = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\WatchLockAI");
            
            if (serviceKey == null)
            {
                var tamperEvent = new TamperAttemptEvent
                {
                    Source = "RegistryCheck",
                    AttackType = "Registry Deletion",
                    Description = "Service registry key has been deleted",
                    Blocked = false
                };
                
                TamperAttemptDetected?.Invoke(this, tamperEvent);
                _logger.LogCritical("TAMPER DETECTED: Service registry key deleted!");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking registry integrity");
        }
    }

    private void CheckServiceConfiguration()
    {
        try
        {
            // Verify service is configured correctly and hasn't been disabled
            using var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_Service WHERE Name='WatchLockAI'");
            
            foreach (ManagementObject service in searcher.Get())
            {
                var startMode = service["StartMode"]?.ToString();
                var state = service["State"]?.ToString();
                
                if (startMode != "Automatic" || state != "Running")
                {
                    var tamperEvent = new TamperAttemptEvent
                    {
                        Source = "ServiceConfig",
                        AttackType = "Service Configuration",
                        Description = $"Service configuration changed: StartMode={startMode}, State={state}",
                        Blocked = false
                    };
                    
                    TamperAttemptDetected?.Invoke(this, tamperEvent);
                    _logger.LogWarning("Service configuration anomaly detected");
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking service configuration");
        }
    }

    private void CheckForSuspiciousProcesses()
    {
        try
        {
            // Check for known security tool terminators or bypass tools
            var suspiciousProcesses = new[]
            {
                "taskkill", "net stop", "sc stop", "wmic process",
                "procexp", "processhacker", "cheatengine"
            };
            
            var processes = Process.GetProcesses();
            
            foreach (var process in processes)
            {
                try
                {
                    var processName = process.ProcessName.ToLower();
                    
                    if (suspiciousProcesses.Any(sp => processName.Contains(sp)))
                    {
                        var tamperEvent = new TamperAttemptEvent
                        {
                            Source = "ProcessMonitor",
                            AttackType = "Suspicious Process",
                            Description = $"Suspicious process detected: {process.ProcessName}",
                            Blocked = false
                        };
                        
                        TamperAttemptDetected?.Invoke(this, tamperEvent);
                        _logger.LogWarning("Suspicious process detected: {ProcessName}", process.ProcessName);
                    }
                }
                catch
                {
                    // Skip processes we can't access
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for suspicious processes");
        }
    }

    private byte[] CalculateFileHash(string filePath)
    {
        try
        {
            if (string.IsNullOrEmpty(filePath) || !File.Exists(filePath))
                return Array.Empty<byte>();
                
            using var sha256 = SHA256.Create();
            using var stream = File.OpenRead(filePath);
            return sha256.ComputeHash(stream);
        }
        catch
        {
            return Array.Empty<byte>();
        }
    }

    private bool CompareHashes(byte[] hash1, byte[] hash2)
    {
        if (hash1.Length != hash2.Length)
            return false;
            
        for (int i = 0; i < hash1.Length; i++)
        {
            if (hash1[i] != hash2[i])
                return false;
        }
        
        return true;
    }
}

/// <summary>
/// Windows system monitoring using ETW and WMI
/// </summary>
public class SystemMonitor : ISystemMonitor
{
    private readonly ILogger<SystemMonitor> _logger;
    private readonly IEventLogger _eventLogger;
    private CancellationTokenSource _cancellationTokenSource;
    private Task _monitoringTask;
    private bool _isMonitoring;

    public bool IsMonitoring => _isMonitoring;
    public event EventHandler<SystemEvent> EventDetected;

    public SystemMonitor(ILogger<SystemMonitor> logger, IEventLogger eventLogger)
    {
        _logger = logger;
        _eventLogger = eventLogger;
    }

    public async Task StartMonitoringAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Starting system monitoring");
            
            _cancellationTokenSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            
            // Start monitoring tasks
            _monitoringTask = Task.Run(() => MonitorSystemEventsAsync(_cancellationTokenSource.Token));
            
            _isMonitoring = true;
            _logger.LogInformation("System monitoring started");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start system monitoring");
            throw;
        }
    }

    public async Task StopMonitoringAsync()
    {
        try
        {
            _logger.LogInformation("Stopping system monitoring");
            
            _isMonitoring = false;
            _cancellationTokenSource?.Cancel();
            
            if (_monitoringTask != null)
            {
                await _monitoringTask;
            }
            
            _cancellationTokenSource?.Dispose();
            _logger.LogInformation("System monitoring stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping system monitoring");
        }
    }

    private async Task MonitorSystemEventsAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                // Monitor process creation
                await MonitorProcessEventsAsync();
                
                // Monitor file system changes
                await MonitorFileSystemEventsAsync();
                
                // Monitor registry changes
                await MonitorRegistryEventsAsync();
                
                // Monitor network connections
                await MonitorNetworkEventsAsync();
                
                // Monitor PowerShell execution
                await MonitorPowerShellEventsAsync();
                
                await Task.Delay(1000, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in system monitoring loop");
                await Task.Delay(5000, cancellationToken);
            }
        }
    }

    private async Task MonitorProcessEventsAsync()
    {
        try
        {
            // Monitor process creation using WMI
            // This is a simplified implementation - production would use ETW
            
            var processes = Process.GetProcesses();
            foreach (var process in processes)
            {
                // Check for new processes (simplified)
                if (process.StartTime > DateTime.Now.AddMinutes(-1))
                {
                    var systemEvent = new SystemEvent
                    {
                        EventId = Guid.NewGuid().ToString(),
                        Timestamp = process.StartTime,
                        Source = "ProcessMonitor",
                        Type = SystemEventType.ProcessStart,
                        ProcessName = process.ProcessName,
                        ProcessId = process.Id,
                        UserName = GetProcessOwner(process.Id)
                    };
                    
                    EventDetected?.Invoke(this, systemEvent);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring process events");
        }
    }

    private async Task MonitorFileSystemEventsAsync()
    {
        try
        {
            // Monitor file system changes
            // This would typically use FileSystemWatcher or USN Journal
            _logger.LogDebug("Monitoring file system events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring file system events");
        }
    }

    private async Task MonitorRegistryEventsAsync()
    {
        try
        {
            // Monitor registry changes
            // This would typically use Registry notification APIs
            _logger.LogDebug("Monitoring registry events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring registry events");
        }
    }

    private async Task MonitorNetworkEventsAsync()
    {
        try
        {
            // Monitor network connections
            // This would typically use ETW network providers
            _logger.LogDebug("Monitoring network events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring network events");
        }
    }

    private async Task MonitorPowerShellEventsAsync()
    {
        try
        {
            // Monitor PowerShell execution
            // This would monitor PowerShell ETW providers
            _logger.LogDebug("Monitoring PowerShell events");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error monitoring PowerShell events");
        }
    }

    private string GetProcessOwner(int processId)
    {
        try
        {
            using var searcher = new ManagementObjectSearcher($"SELECT * FROM Win32_Process WHERE ProcessId = {processId}");
            foreach (ManagementObject process in searcher.Get())
            {
                var args = new string[2];
                if (process.InvokeMethod("GetOwner", args) == 0)
                {
                    return $"{args[1]}\{args[0]}";
                }
            }
        }
        catch
        {
            // Ignore errors getting process owner
        }
        
        return "Unknown";
    }
}
