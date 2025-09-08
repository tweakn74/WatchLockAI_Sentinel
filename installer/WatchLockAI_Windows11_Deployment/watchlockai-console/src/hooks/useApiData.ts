import { useState, useEffect, useCallback } from 'react';
import { apiService, Organization, Agent, Threat, Investigation } from '../lib/api';

// Generic hook for API data fetching
function useApiData<T>(fetchFn: () => Promise<{ data: T | null; error: string | null; success: boolean }>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchFn();
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.error);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Organizations hook
export function useOrganizations() {
  return useApiData<Organization[]>(() => apiService.getOrganizations());
}

// Agents hook
export function useAgents(organizationId?: string) {
  return useApiData<Agent[]>(() => apiService.getAgents(organizationId));
}

// Threats hook
export function useThreats(organizationId?: string) {
  return useApiData<Threat[]>(() => apiService.getThreats(organizationId));
}

// Investigations hook
export function useInvestigations(organizationId?: string) {
  return useApiData<Investigation[]>(() => apiService.getInvestigations(organizationId));
}

// Real-time data hook with automatic refresh
export function useRealTimeData<T>(
  fetchFn: () => Promise<{ data: T | null; error: string | null; success: boolean }>,
  interval: number = 30000 // 30 seconds default
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await fetchFn();
      if (result.success) {
        setData(result.data);
        setLastUpdate(new Date());
        setError(null);
      } else {
        setError(result.error);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up interval for real-time updates
    const intervalId = setInterval(fetchData, interval);

    return () => clearInterval(intervalId);
  }, [fetchData, interval]);

  return {
    data,
    loading,
    error,
    lastUpdate,
    refetch: fetchData
  };
}

// Mutation hooks for data modification
export function useCreateThreat() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createThreat = useCallback(async (threat: Partial<Threat>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.createThreat(threat);
      if (!result.success) {
        setError(result.error);
        return null;
      }
      return result.data;
    } catch (err: any) {
      setError(err.message || 'Failed to create threat');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    createThreat,
    loading,
    error
  };
}

export function useUpdateThreatStatus() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateStatus = useCallback(async (threatId: string, status: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.updateThreatStatus(threatId, status);
      if (!result.success) {
        setError(result.error);
        return false;
      }
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to update threat status');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    updateStatus,
    loading,
    error
  };
}

export function useUpdateAgentStatus() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateStatus = useCallback(async (agentId: string, status: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.updateAgentStatus(agentId, status);
      if (!result.success) {
        setError(result.error);
        return false;
      }
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to update agent status');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    updateStatus,
    loading,
    error
  };
}

// Dashboard metrics hook
export function useDashboardMetrics(organizationId?: string) {
  const { data: threats } = useRealTimeData<Threat[]>(
    () => apiService.getThreats(organizationId),
    15000 // 15 seconds for threats
  );
  
  const { data: agents } = useRealTimeData<Agent[]>(
    () => apiService.getAgents(organizationId),
    30000 // 30 seconds for agents
  );

  const metrics = {
    threats: {
      total: threats?.length || 0,
      critical: threats?.filter(t => t.severity === 'critical').length || 0,
      high: threats?.filter(t => t.severity === 'high').length || 0,
      open: threats?.filter(t => t.status === 'open').length || 0,
      investigating: threats?.filter(t => t.status === 'investigating').length || 0
    },
    agents: {
      total: agents?.length || 0,
      online: agents?.filter(a => a.status === 'online').length || 0,
      offline: agents?.filter(a => a.status === 'offline').length || 0,
      error: agents?.filter(a => a.status === 'error').length || 0
    },
    security: {
      avgThreatScore: threats?.reduce((sum, t) => sum + t.threat_score, 0) / (threats?.length || 1) || 0,
      avgConfidence: threats?.reduce((sum, t) => sum + t.confidence_score, 0) / (threats?.length || 1) || 0,
      detectionRate: 85, // Calculate based on actual data
      responseTime: 12 // Average response time in minutes
    }
  };

  return {
    metrics,
    threats,
    agents,
    loading: false
  };
}

// API health check hook
export function useApiHealth() {
  const [health, setHealth] = useState<{ supabase: boolean; local: boolean }>({ 
    supabase: false, 
    local: true 
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      setLoading(true);
      try {
        const healthStatus = await apiService.healthCheck();
        setHealth(healthStatus);
      } catch (error) {
        console.error('Health check failed:', error);
        setHealth({ supabase: false, local: true });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    
    // Check health every 5 minutes
    const interval = setInterval(checkHealth, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  return { health, loading };
}