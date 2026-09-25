using System;
using System.Threading;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.AI;

/// <summary>
/// AI-powered threat analysis and behavioral learning engine
/// </summary>
public interface IAIBrain
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task StopAsync();
    Task<ThreatEvent> AnalyzeSystemEventAsync(SystemEvent systemEvent);
    Task<double> CalculateAnomalyScoreAsync(SystemEvent systemEvent);
    Task UpdateBehavioralBaselineAsync(BehavioralBaseline baseline);
    Task<string> GenerateIncidentNarrativeAsync(ThreatEvent threat);
}

/// <summary>
/// Behavioral analysis for user and system patterns
/// </summary>
public interface IBehavioralAnalyzer
{
    Task<BehavioralBaseline> CreateBaselineAsync(string entityId, string entityType);
    Task<double> CalculateDeviationAsync(BehavioralBaseline baseline, SystemEvent systemEvent);
    Task UpdateBaselineAsync(BehavioralBaseline baseline, SystemEvent systemEvent);
    Task<bool> IsAnomalousAsync(SystemEvent systemEvent);
}
