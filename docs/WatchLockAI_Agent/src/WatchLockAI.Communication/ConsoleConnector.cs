using Microsoft.Extensions.Logging;
using Grpc.Net.Client;
using Newtonsoft.Json;
using System;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;
using WatchLockAI.Forensics;

namespace WatchLockAI.Communication;

/// <summary>
/// Secure communication with WatchLockAI management console
/// </summary>
public class ConsoleConnector : IConsoleConnector
{
    private readonly ILogger<ConsoleConnector> _logger;
    private readonly IConfigurationManager _configManager;
    private readonly IEventLogger _eventLogger;
    private readonly HttpClient _httpClient;
    private Timer _heartbeatTimer;
    private bool _isConnected;
    private string _consoleEndpoint;
    private string _agentId;

    public bool IsConnected => _isConnected;
    public event EventHandler<ConsoleMessage> MessageReceived;

    public ConsoleConnector(
        ILogger<ConsoleConnector> logger,
        IConfigurationManager configManager,
        IEventLogger eventLogger)
    {
        _logger = logger;
        _configManager = configManager;
        _eventLogger = eventLogger;
        _httpClient = new HttpClient();
        _agentId = Environment.MachineName + "_" + Guid.NewGuid().ToString("N")[..8];
    }

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Initializing console connector");
            
            _consoleEndpoint = _configManager.GetSetting("ConsoleEndpoint", "https://console.watchlockai.com");
            
            // Configure HTTP client
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "WatchLockAI-Agent/1.0");
            _httpClient.DefaultRequestHeaders.Add("X-Agent-Id", _agentId);
            
            // Test connection
            await TestConnectionAsync();
            
            // Start heartbeat
            var heartbeatInterval = _configManager.GetSetting("HeartbeatInterval", 60);
            _heartbeatTimer = new Timer(HeartbeatCallback, null, 
                TimeSpan.Zero, TimeSpan.FromSeconds(heartbeatInterval));
            
            _isConnected = true;
            _logger.LogInformation("Console connector initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize console connector");
            _isConnected = false;
            // Don't throw - allow agent to operate in offline mode
        }
    }

    public async Task DisconnectAsync()
    {
        try
        {
            _logger.LogInformation("Disconnecting from console");
            
            _isConnected = false;
            _heartbeatTimer?.Dispose();
            
            // Send disconnect notification
            await SendDisconnectNotificationAsync();
            
            _httpClient?.Dispose();
            _logger.LogInformation("Disconnected from console");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error disconnecting from console");
        }
    }

    public async Task ReportThreatAsync(ThreatEvent threat, Investigation investigation, ResponseResult response)
    {
        try
        {
            if (!_isConnected)
            {
                _logger.LogWarning("Cannot report threat - not connected to console");
                return;
            }

            _logger.LogInformation("Reporting threat {ThreatId} to console", threat.Id);

            var report = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Threat = threat,
                Investigation = investigation,
                Response = response
            };

            var json = JsonConvert.SerializeObject(report);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response_http = await _httpClient.PostAsync($"{_consoleEndpoint}/api/threats", content);
            
            if (response_http.IsSuccessStatusCode)
            {
                _logger.LogInformation("Threat report sent successfully");
            }
            else
            {
                _logger.LogWarning("Failed to send threat report: {StatusCode}", response_http.StatusCode);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reporting threat to console");
        }
    }

    public async Task SendHeartbeatAsync()
    {
        try
        {
            if (!_isConnected) return;

            var heartbeat = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Status = "Online",
                Version = "1.0.0",
                SystemInfo = new
                {
                    MachineName = Environment.MachineName,
                    OSVersion = Environment.OSVersion.ToString(),
                    ProcessorCount = Environment.ProcessorCount,
                    MemoryUsage = GC.GetTotalMemory(false)
                }
            };

            var json = JsonConvert.SerializeObject(heartbeat);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_consoleEndpoint}/api/heartbeat", content);
            
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Heartbeat failed: {StatusCode}", response.StatusCode);
                _isConnected = false;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending heartbeat");
            _isConnected = false;
        }
    }

    public async Task<PolicyUpdate> CheckForPolicyUpdatesAsync()
    {
        try
        {
            if (!_isConnected) return null;

            var response = await _httpClient.GetAsync($"{_consoleEndpoint}/api/policies/{_agentId}");
            
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var policy = JsonConvert.DeserializeObject<PolicyUpdate>(json);
                
                if (policy != null)
                {
                    _logger.LogInformation("Received policy update: {PolicyType}", policy.PolicyType);
                    return policy;
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for policy updates");
        }
        
        return null;
    }

    private async Task TestConnectionAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_consoleEndpoint}/api/health");
            
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Successfully connected to console at {Endpoint}", _consoleEndpoint);
            }
            else
            {
                throw new InvalidOperationException($"Console health check failed: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to connect to console at {Endpoint}", _consoleEndpoint);
            throw;
        }
    }

    private void HeartbeatCallback(object state)
    {
        try
        {
            _ = Task.Run(SendHeartbeatAsync);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in heartbeat callback");
        }
    }

    private async Task SendDisconnectNotificationAsync()
    {
        try
        {
            var notification = new
            {
                AgentId = _agentId,
                Timestamp = DateTime.UtcNow,
                Status = "Disconnecting"
            };

            var json = JsonConvert.SerializeObject(notification);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            await _httpClient.PostAsync($"{_consoleEndpoint}/api/disconnect", content);
        }
        catch
        {
            // Ignore errors during disconnect
        }
    }
}
