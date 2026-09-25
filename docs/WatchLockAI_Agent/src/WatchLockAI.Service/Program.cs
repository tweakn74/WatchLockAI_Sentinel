using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Serilog;
using WatchLockAI.Core;
using WatchLockAI.AI;
using WatchLockAI.Detection;
using WatchLockAI.Response;
using WatchLockAI.Forensics;
using WatchLockAI.Integration;
using WatchLockAI.Security;
using WatchLockAI.Communication;
using WatchLockAI.Common;

namespace WatchLockAI.Service;

/// <summary>
/// WatchLockAI Windows Service Entry Point
/// Autonomous AI-powered cybersecurity endpoint agent
/// </summary>
public class Program
{
    public static void Main(string[] args)
    {
        // Configure Serilog for system-wide logging
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Information()
            .WriteTo.File("logs/watchlockai-.log", rollingInterval: RollingInterval.Day)
            .WriteTo.EventLog("WatchLockAI", manageEventSource: true)
            .CreateLogger();

        try
        {
            Log.Information("WatchLockAI Service starting up");
            CreateHostBuilder(args).Build().Run();
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "WatchLockAI Service terminated unexpectedly");
        }
        finally
        {
            Log.CloseAndFlush();
        }
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .UseWindowsService(options =>
            {
                options.ServiceName = "WatchLockAI";
            })
            .UseSerilog()
            .ConfigureServices((hostContext, services) =>
            {
                // Core services
                services.AddHostedService<WatchLockAIWorker>();
                services.AddSingleton<ICoreEngine, CoreEngine>();
                
                // AI and Detection
                services.AddSingleton<IAIBrain, AIBrain>();
                services.AddSingleton<IThreatDetectionEngine, ThreatDetectionEngine>();
                services.AddSingleton<IBehavioralAnalyzer, BehavioralAnalyzer>();
                
                // Response and Forensics
                services.AddSingleton<IResponseEngine, ResponseEngine>();
                services.AddSingleton<IForensicsEngine, ForensicsEngine>();
                services.AddSingleton<IAccountSentinel, AccountSentinel>();
                
                // Security and Communication
                services.AddSingleton<ITamperproofManager, TamperproofManager>();
                services.AddSingleton<ISystemMonitor, SystemMonitor>();
                services.AddSingleton<IConsoleConnector, ConsoleConnector>();
                
                // Integration services
                services.AddSingleton<IDefenderIntegration, DefenderIntegration>();
                services.AddSingleton<IAzureIntegration, AzureIntegration>();
                services.AddSingleton<IFirewallController, FirewallController>();
                
                // Common utilities
                services.AddSingleton<IConfigurationManager, ConfigurationManager>();
                services.AddSingleton<IEventLogger, EventLogger>();
            });
}

/// <summary>
/// Main worker service that orchestrates all WatchLockAI components
/// </summary>
public class WatchLockAIWorker : BackgroundService
{
    private readonly ILogger<WatchLockAIWorker> _logger;
    private readonly ICoreEngine _coreEngine;
    private readonly ITamperproofManager _tamperproofManager;

    public WatchLockAIWorker(
        ILogger<WatchLockAIWorker> logger,
        ICoreEngine coreEngine,
        ITamperproofManager tamperproofManager)
    {
        _logger = logger;
        _coreEngine = coreEngine;
        _tamperproofManager = tamperproofManager;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("WatchLockAI Worker starting execution");

        try
        {
            // Initialize tamperproofing first
            await _tamperproofManager.InitializeAsync();
            
            // Start core engine
            await _coreEngine.StartAsync(stoppingToken);
            
            _logger.LogInformation("WatchLockAI Agent fully operational");

            // Keep running until cancellation requested
            while (!stoppingToken.IsCancellationRequested)
            {
                await Task.Delay(5000, stoppingToken); // Heartbeat every 5 seconds
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Critical error in WatchLockAI Worker");
            throw;
        }
        finally
        {
            await _coreEngine.StopAsync();
            _logger.LogInformation("WatchLockAI Worker stopped");
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("WatchLockAI Worker stop requested");
        await base.StopAsync(cancellationToken);
    }
}