using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.AI;
using WatchLockAI.Detection;
using WatchLockAI.Response;
using WatchLockAI.Forensics;
using WatchLockAI.Security;
using WatchLockAI.Communication;
using WatchLockAI.Common;

namespace WatchLockAI.Core;

/// <summary>
/// Main orchestration engine that coordinates all WatchLockAI subsystems
/// </summary>
public class CoreEngine : ICoreEngine
{
    private readonly ILogger<CoreEngine> _logger;
    private readonly IAIBrain _aiBrain;
    private readonly IThreatDetectionEngine _threatDetection;
    private readonly IResponseEngine _responseEngine;
    private readonly IForensicsEngine _forensicsEngine;
    private readonly ISystemMonitor _systemMonitor;
    private readonly IConsoleConnector _consoleConnector;
    private readonly IEventLogger _eventLogger;
    
    private CancellationTokenSource _cancellationTokenSource;
    private bool _isRunning;

    public bool IsRunning => _isRunning;
    
    public event EventHandler<ThreatEvent> ThreatDetected;
    public event EventHandler<SystemEvent> SystemEventOccurred;

    public CoreEngine(
        ILogger<CoreEngine> logger,
        IAIBrain aiBrain,
        IThreatDetectionEngine threatDetection,
        IResponseEngine responseEngine,
        IForensicsEngine forensicsEngine,
        ISystemMonitor systemMonitor,
        IConsoleConnector consoleConnector,
        IEventLogger eventLogger)
    {
        _logger = logger;
        _aiBrain = aiBrain;
        _threatDetection = threatDetection;
        _responseEngine = responseEngine;
        _forensicsEngine = forensicsEngine;
        _systemMonitor = systemMonitor;
        _consoleConnector = consoleConnector;
        _eventLogger = eventLogger;
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Starting WatchLockAI Core Engine");
            
            _cancellationTokenSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            
            // Initialize all subsystems in order
            await InitializeSubsystemsAsync(_cancellationTokenSource.Token);
            
            // Wire up event handlers
            SetupEventHandlers();
            
            // Start monitoring
            await _systemMonitor.StartMonitoringAsync(_cancellationTokenSource.Token);
            
            _isRunning = true;
            _logger.LogInformation("WatchLockAI Core Engine started successfully");
            
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.SystemModification,
                Source = "CoreEngine",
                Message = "WatchLockAI Agent started and operational"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start WatchLockAI Core Engine");
            await StopAsync();
            throw;
        }
    }

    public async Task StopAsync()
    {
        try
        {
            _logger.LogInformation("Stopping WatchLockAI Core Engine");
            
            _isRunning = false;
            
            // Stop monitoring first
            await _systemMonitor.StopMonitoringAsync();
            
            // Stop all subsystems
            await StopSubsystemsAsync();
            
            _cancellationTokenSource?.Cancel();
            _cancellationTokenSource?.Dispose();
            
            _logger.LogInformation("WatchLockAI Core Engine stopped");
            
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.SystemModification,
                Source = "CoreEngine",
                Message = "WatchLockAI Agent stopped"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping WatchLockAI Core Engine");
        }
    }

    private async Task InitializeSubsystemsAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Initializing WatchLockAI subsystems");
        
        // Initialize AI Brain first
        await _aiBrain.InitializeAsync(cancellationToken);
        _logger.LogDebug("AI Brain initialized");
        
        // Initialize threat detection
        await _threatDetection.InitializeAsync(cancellationToken);
        _logger.LogDebug("Threat Detection Engine initialized");
        
        // Initialize response engine
        await _responseEngine.InitializeAsync(cancellationToken);
        _logger.LogDebug("Response Engine initialized");
        
        // Initialize forensics engine
        await _forensicsEngine.InitializeAsync(cancellationToken);
        _logger.LogDebug("Forensics Engine initialized");
        
        // Initialize console connector
        await _consoleConnector.InitializeAsync(cancellationToken);
        _logger.LogDebug("Console Connector initialized");
        
        _logger.LogInformation("All subsystems initialized successfully");
    }

    private async Task StopSubsystemsAsync()
    {
        try
        {
            await _consoleConnector.DisconnectAsync();
            await _forensicsEngine.StopAsync();
            await _responseEngine.StopAsync();
            await _threatDetection.StopAsync();
            await _aiBrain.StopAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping subsystems");
        }
    }

    private void SetupEventHandlers()
    {
        // System monitor events
        _systemMonitor.EventDetected += async (sender, systemEvent) =>
        {
            try
            {
                SystemEventOccurred?.Invoke(this, systemEvent);
                
                // Send to AI brain for analysis
                var threatEvent = await _aiBrain.AnalyzeSystemEventAsync(systemEvent);
                
                if (threatEvent != null)
                {
                    await HandleThreatEventAsync(threatEvent);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error handling system event: {EventType}", systemEvent.Type);
            }
        };
        
        // Threat detection events
        _threatDetection.ThreatDetected += async (sender, threat) =>
        {
            await HandleThreatEventAsync(threat);
        };
    }

    private async Task HandleThreatEventAsync(ThreatEvent threatEvent)
    {
        try
        {
            _logger.LogWarning("Threat detected: {Type} - {Description}", 
                threatEvent.Type, threatEvent.Description);
            
            ThreatDetected?.Invoke(this, threatEvent);
            
            // Log security event
            await _eventLogger.LogSecurityEventAsync(new SecurityEvent
            {
                Type = SecurityEventType.ThreatDetected,
                Source = threatEvent.Source,
                Message = threatEvent.Description
            });
            
            // Start forensic investigation
            var investigation = await _forensicsEngine.StartInvestigationAsync(threatEvent);
            
            // Execute response if auto-response is enabled
            var responseResult = await _responseEngine.RespondToThreatAsync(threatEvent);
            
            // Report to console
            await _consoleConnector.ReportThreatAsync(threatEvent, investigation, responseResult);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling threat event: {ThreatId}", threatEvent.Id);
        }
    }
}
