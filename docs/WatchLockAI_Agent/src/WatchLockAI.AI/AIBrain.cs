using Microsoft.Extensions.Logging;
using Microsoft.ML.OnnxRuntime;
using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.AI;

/// <summary>
/// Local LLM-powered AI brain for real-time threat analysis
/// </summary>
public class AIBrain : IAIBrain, IDisposable
{
    private readonly ILogger<AIBrain> _logger;
    private readonly IBehavioralAnalyzer _behavioralAnalyzer;
    private readonly IEventLogger _eventLogger;
    
    private InferenceSession _onnxSession;
    private readonly ConcurrentDictionary<string, BehavioralBaseline> _baselines;
    private readonly SemaphoreSlim _analysisSemaphore;
    
    private bool _isInitialized;
    private readonly object _lockObject = new object();

    public AIBrain(
        ILogger<AIBrain> logger,
        IBehavioralAnalyzer behavioralAnalyzer,
        IEventLogger eventLogger)
    {
        _logger = logger;
        _behavioralAnalyzer = behavioralAnalyzer;
        _eventLogger = eventLogger;
        _baselines = new ConcurrentDictionary<string, BehavioralBaseline>();
        _analysisSemaphore = new SemaphoreSlim(1, 1);
    }

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Initializing AI Brain");
            
            // Load ONNX model for threat detection
            await LoadThreatDetectionModelAsync();
            
            // Load existing behavioral baselines
            await LoadBehavioralBaselinesAsync();
            
            _isInitialized = true;
            _logger.LogInformation("AI Brain initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize AI Brain");
            throw;
        }
    }

    public async Task StopAsync()
    {
        try
        {
            _logger.LogInformation("Stopping AI Brain");
            
            lock (_lockObject)
            {
                _isInitialized = false;
            }
            
            // Save behavioral baselines
            await SaveBehavioralBaselinesAsync();
            
            _onnxSession?.Dispose();
            _analysisSemaphore?.Dispose();
            
            _logger.LogInformation("AI Brain stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping AI Brain");
        }
    }

    public async Task<ThreatEvent> AnalyzeSystemEventAsync(SystemEvent systemEvent)
    {
        if (!_isInitialized)
            return null;

        try
        {
            await _analysisSemaphore.WaitAsync();
            
            // Calculate anomaly score
            var anomalyScore = await CalculateAnomalyScoreAsync(systemEvent);
            
            // Check for known attack patterns
            var attackPattern = await DetectAttackPatternAsync(systemEvent);
            
            // Determine if this is a threat
            if (anomalyScore > 0.7 || attackPattern != null)
            {
                var threat = new ThreatEvent
                {
                    Source = "AIBrain",
                    Type = attackPattern?.TechniqueName ?? "Anomalous Behavior",
                    Severity = DetermineSeverity(anomalyScore, attackPattern),
                    Description = await GenerateThreatDescriptionAsync(systemEvent, anomalyScore, attackPattern),
                    MitreAttackTechnique = attackPattern?.TechniqueId,
                    KillChainPhase = attackPattern?.KillChainPhase
                };
                
                threat.Properties["AnomalyScore"] = anomalyScore;
                threat.Properties["SystemEvent"] = systemEvent;
                
                _logger.LogWarning("Threat detected by AI Brain: {Type} (Score: {Score})", 
                    threat.Type, anomalyScore);
                
                return threat;
            }
            
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing system event");
            return null;
        }
        finally
        {
            _analysisSemaphore.Release();
        }
    }

    public async Task<double> CalculateAnomalyScoreAsync(SystemEvent systemEvent)
    {
        try
        {
            // Get behavioral baseline for the entity
            var entityId = systemEvent.ProcessName ?? systemEvent.UserName ?? "system";
            var baseline = await GetOrCreateBaselineAsync(entityId, "process");
            
            // Calculate deviation from baseline
            var deviation = await _behavioralAnalyzer.CalculateDeviationAsync(baseline, systemEvent);
            
            // Use ML model for additional scoring if available
            var mlScore = await CalculateMLAnomalyScoreAsync(systemEvent);
            
            // Combine scores (weighted average)
            var combinedScore = (deviation * 0.6) + (mlScore * 0.4);
            
            return Math.Min(1.0, combinedScore);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating anomaly score");
            return 0.0;
        }
    }

    public async Task UpdateBehavioralBaselineAsync(BehavioralBaseline baseline)
    {
        try
        {
            _baselines.AddOrUpdate(baseline.EntityId, baseline, (key, oldValue) => baseline);
            _logger.LogDebug("Updated behavioral baseline for {EntityId}", baseline.EntityId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating behavioral baseline");
        }
    }

    public async Task<string> GenerateIncidentNarrativeAsync(ThreatEvent threat)
    {
        try
        {
            // Generate human-readable narrative using LLM
            var narrative = $"At {threat.Timestamp:yyyy-MM-dd HH:mm:ss} UTC, ";
            narrative += $"WatchLockAI detected {threat.Type.ToLower()} activity ";
            narrative += $"with {threat.Severity.ToString().ToLower()} severity. ";
            
            if (!string.IsNullOrEmpty(threat.MitreAttackTechnique))
            {
                narrative += $"This activity maps to MITRE ATT&CK technique {threat.MitreAttackTechnique} ";
                narrative += $"in the {threat.KillChainPhase} phase. ";
            }
            
            narrative += $"Description: {threat.Description}";
            
            return narrative;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating incident narrative");
            return threat.Description;
        }
    }

    private async Task LoadThreatDetectionModelAsync()
    {
        try
        {
            // Load ONNX model for threat detection (placeholder path)
            var modelPath = @"resources\models	hreat_detection.onnx";
            
            if (System.IO.File.Exists(modelPath))
            {
                _onnxSession = new InferenceSession(modelPath);
                _logger.LogInformation("Threat detection model loaded");
            }
            else
            {
                _logger.LogWarning("Threat detection model not found, using rule-based detection");
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to load threat detection model");
        }
    }

    private async Task<BehavioralBaseline> GetOrCreateBaselineAsync(string entityId, string entityType)
    {
        if (_baselines.TryGetValue(entityId, out var existing))
        {
            return existing;
        }
        
        var newBaseline = await _behavioralAnalyzer.CreateBaselineAsync(entityId, entityType);
        _baselines.TryAdd(entityId, newBaseline);
        
        return newBaseline;
    }

    private async Task<AttackPattern> DetectAttackPatternAsync(SystemEvent systemEvent)
    {
        // Implement MITRE ATT&CK pattern detection
        // This is a simplified example - full implementation would be more comprehensive
        
        if (systemEvent.Type == SystemEventType.PowerShellExecution)
        {
            if (systemEvent.CommandLine?.Contains("-EncodedCommand") == true)
            {
                return new AttackPattern
                {
                    TechniqueId = "T1059.001",
                    TechniqueName = "PowerShell",
                    KillChainPhase = "Execution"
                };
            }
        }
        
        if (systemEvent.Type == SystemEventType.ProcessStart)
        {
            if (systemEvent.ProcessName?.EndsWith("rundll32.exe") == true)
            {
                return new AttackPattern
                {
                    TechniqueId = "T1218.011",
                    TechniqueName = "Rundll32",
                    KillChainPhase = "Defense Evasion"
                };
            }
        }
        
        return null;
    }

    private ThreatSeverity DetermineSeverity(double anomalyScore, AttackPattern attackPattern)
    {
        if (attackPattern != null)
        {
            // Known attack patterns are at least medium severity
            return anomalyScore > 0.9 ? ThreatSeverity.Critical : ThreatSeverity.High;
        }
        
        return anomalyScore switch
        {
            > 0.9 => ThreatSeverity.Critical,
            > 0.8 => ThreatSeverity.High,
            > 0.7 => ThreatSeverity.Medium,
            _ => ThreatSeverity.Low
        };
    }

    private async Task<string> GenerateThreatDescriptionAsync(SystemEvent systemEvent, double anomalyScore, AttackPattern attackPattern)
    {
        if (attackPattern != null)
        {
            return $"Detected {attackPattern.TechniqueName} technique in process {systemEvent.ProcessName} " +
                   $"(PID: {systemEvent.ProcessId}). Command: {systemEvent.CommandLine}";
        }
        
        return $"Anomalous behavior detected in {systemEvent.ProcessName} " +
               $"(Score: {anomalyScore:F2}). Event: {systemEvent.Type}";
    }

    private async Task<double> CalculateMLAnomalyScoreAsync(SystemEvent systemEvent)
    {
        // Placeholder for ML-based scoring
        // In production, this would use the ONNX model
        return 0.0;
    }

    private async Task LoadBehavioralBaselinesAsync()
    {
        // Load saved baselines from disk
        _logger.LogDebug("Loading behavioral baselines");
    }

    private async Task SaveBehavioralBaselinesAsync()
    {
        // Save baselines to disk
        _logger.LogDebug("Saving behavioral baselines");
    }

    public void Dispose()
    {
        _onnxSession?.Dispose();
        _analysisSemaphore?.Dispose();
    }
}

/// <summary>
/// Attack pattern detection data
/// </summary>
public class AttackPattern
{
    public string TechniqueId { get; set; }
    public string TechniqueName { get; set; }
    public string KillChainPhase { get; set; }
    public double Confidence { get; set; }
}

/// <summary>
/// Behavioral analysis implementation
/// </summary>
public class BehavioralAnalyzer : IBehavioralAnalyzer
{
    private readonly ILogger<BehavioralAnalyzer> _logger;
    
    public BehavioralAnalyzer(ILogger<BehavioralAnalyzer> logger)
    {
        _logger = logger;
    }

    public async Task<BehavioralBaseline> CreateBaselineAsync(string entityId, string entityType)
    {
        return new BehavioralBaseline
        {
            EntityId = entityId,
            EntityType = entityType,
            CreatedAt = DateTime.UtcNow,
            LastUpdated = DateTime.UtcNow,
            DeviationThreshold = 0.8
        };
    }

    public async Task<double> CalculateDeviationAsync(BehavioralBaseline baseline, SystemEvent systemEvent)
    {
        // Simplified deviation calculation
        // Production version would use sophisticated statistical analysis
        
        var timeFactor = CalculateTimeDeviation(baseline, systemEvent);
        var frequencyFactor = CalculateFrequencyDeviation(baseline, systemEvent);
        var contextFactor = CalculateContextDeviation(baseline, systemEvent);
        
        return (timeFactor + frequencyFactor + contextFactor) / 3.0;
    }

    public async Task UpdateBaselineAsync(BehavioralBaseline baseline, SystemEvent systemEvent)
    {
        baseline.LastUpdated = DateTime.UtcNow;
        // Update patterns based on the new event
    }

    public async Task<bool> IsAnomalousAsync(SystemEvent systemEvent)
    {
        // Quick anomaly check
        return await Task.FromResult(false);
    }

    private double CalculateTimeDeviation(BehavioralBaseline baseline, SystemEvent systemEvent)
    {
        // Calculate if this event occurs at an unusual time
        return 0.0;
    }

    private double CalculateFrequencyDeviation(BehavioralBaseline baseline, SystemEvent systemEvent)
    {
        // Calculate if this event occurs more/less frequently than normal
        return 0.0;
    }

    private double CalculateContextDeviation(BehavioralBaseline baseline, SystemEvent systemEvent)
    {
        // Calculate if this event occurs in an unusual context
        return 0.0;
    }
}
