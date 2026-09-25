using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Collections.Concurrent;
using System.IO;
using System.Threading.Tasks;
using WatchLockAI.Common;

namespace WatchLockAI.Common;

/// <summary>
/// Secure configuration management with encryption
/// </summary>
public class ConfigurationManager : IConfigurationManager
{
    private readonly ILogger<ConfigurationManager> _logger;
    private readonly ConcurrentDictionary<string, object> _settings;
    private readonly string _configFile;
    private readonly object _lockObject = new object();

    public ConfigurationManager(ILogger<ConfigurationManager> logger)
    {
        _logger = logger;
        _settings = new ConcurrentDictionary<string, object>();
        _configFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), 
                                   "WatchLockAI", "config.enc");
        
        // Ensure config directory exists
        Directory.CreateDirectory(Path.GetDirectoryName(_configFile));
    }

    public T GetSetting<T>(string key, T defaultValue = default)
    {
        try
        {
            if (_settings.TryGetValue(key, out var value))
            {
                if (value is T directValue)
                    return directValue;
                
                // Try to convert
                return (T)Convert.ChangeType(value, typeof(T));
            }
            
            return defaultValue;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to get setting {Key}, returning default", key);
            return defaultValue;
        }
    }

    public void SetSetting<T>(string key, T value)
    {
        _settings.AddOrUpdate(key, value, (k, v) => value);
        _logger.LogDebug("Setting updated: {Key}", key);
    }

    public async Task SaveAsync()
    {
        try
        {
            lock (_lockObject)
            {
                var json = JsonConvert.SerializeObject(_settings, Formatting.Indented);
                var encrypted = EncryptData(json);
                File.WriteAllBytes(_configFile, encrypted);
            }
            
            _logger.LogInformation("Configuration saved successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save configuration");
            throw;
        }
    }

    public async Task LoadAsync()
    {
        try
        {
            if (!File.Exists(_configFile))
            {
                await LoadDefaultSettingsAsync();
                return;
            }

            var encrypted = File.ReadAllBytes(_configFile);
            var json = DecryptData(encrypted);
            var settings = JsonConvert.DeserializeObject<ConcurrentDictionary<string, object>>(json);
            
            _settings.Clear();
            foreach (var kvp in settings)
            {
                _settings.TryAdd(kvp.Key, kvp.Value);
            }
            
            _logger.LogInformation("Configuration loaded successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load configuration, using defaults");
            await LoadDefaultSettingsAsync();
        }
    }

    private async Task LoadDefaultSettingsAsync()
    {
        // Default settings
        SetSetting("LogLevel", "Information");
        SetSetting("ConsoleEndpoint", "https://console.watchlockai.com");
        SetSetting("UpdateInterval", 60);
        SetSetting("MemoryLimit", 512);
        SetSetting("ThreatDetectionEnabled", true);
        SetSetting("BehavioralLearningEnabled", true);
        SetSetting("AutoResponseEnabled", false);
        SetSetting("ForensicsEnabled", true);
        SetSetting("TamperproofEnabled", true);
        
        await SaveAsync();
    }

    private byte[] EncryptData(string data)
    {
        // Implement DPAPI encryption for Windows
        return System.Security.Cryptography.ProtectedData.Protect(
            System.Text.Encoding.UTF8.GetBytes(data),
            null,
            System.Security.Cryptography.DataProtectionScope.LocalMachine);
    }

    private string DecryptData(byte[] encryptedData)
    {
        // Implement DPAPI decryption for Windows
        var decrypted = System.Security.Cryptography.ProtectedData.Unprotect(
            encryptedData,
            null,
            System.Security.Cryptography.DataProtectionScope.LocalMachine);
        
        return System.Text.Encoding.UTF8.GetString(decrypted);
    }
}

/// <summary>
/// Centralized event logging with security focus
/// </summary>
public class EventLogger : IEventLogger
{
    private readonly ILogger<EventLogger> _logger;
    private readonly ConcurrentQueue<SecurityEvent> _eventQueue;

    public EventLogger(ILogger<EventLogger> logger)
    {
        _logger = logger;
        _eventQueue = new ConcurrentQueue<SecurityEvent>();
    }

    public async Task LogInformationAsync(string message, object data = null)
    {
        _logger.LogInformation("WatchLockAI: {Message} {@Data}", message, data);
    }

    public async Task LogWarningAsync(string message, object data = null)
    {
        _logger.LogWarning("WatchLockAI Warning: {Message} {@Data}", message, data);
    }

    public async Task LogErrorAsync(string message, Exception exception = null, object data = null)
    {
        _logger.LogError(exception, "WatchLockAI Error: {Message} {@Data}", message, data);
    }

    public async Task LogSecurityEventAsync(SecurityEvent securityEvent)
    {
        _eventQueue.Enqueue(securityEvent);
        
        _logger.LogInformation("Security Event: {Type} - {Message} from {Source}",
            securityEvent.Type, securityEvent.Message, securityEvent.Source);
            
        // TODO: Send to console/SIEM
    }
}
