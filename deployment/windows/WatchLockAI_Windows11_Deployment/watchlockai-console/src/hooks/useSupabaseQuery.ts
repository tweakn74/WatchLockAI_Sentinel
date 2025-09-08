import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';
import { useAuth } from '../lib/auth';

// Custom hook for Supabase edge function calls
export function useEdgeFunction() {
  const { user, session } = useAuth();
  const queryClient = useQueryClient();

  const callFunction = useMutation({
    mutationFn: async ({ functionName, payload }: { functionName: string; payload: any }) => {
      if (!user) throw new Error('User not authenticated');

      const { data, error } = await supabase.functions.invoke(functionName, {
        body: { ...payload, user_id: user.id },
        headers: {
          Authorization: `Bearer ${session?.access_token}`
        }
      });

      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      // Invalidate relevant queries after successful mutations
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['investigations'] });
      queryClient.invalidateQueries({ queryKey: ['responses'] });
    }
  });

  return callFunction;
}

// Hook for fetching threats
export function useThreats(organizationId: string, status?: string) {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['threats', organizationId, status],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');

      const { data, error } = await supabase.functions.invoke('threat-monitor', {
        body: {
          action: 'get_threats',
          threat_data: {
            organization_id: organizationId,
            status: status || 'open',
            limit: 100
          }
        }
      });

      if (error) throw error;
      return data.data;
    },
    enabled: !!user && !!organizationId,
    refetchInterval: 30000 // Refresh every 30 seconds
  });
}

// Hook for fetching agents
export function useAgents(organizationId: string, status?: string) {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['agents', organizationId, status],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');

      const { data, error } = await supabase.functions.invoke('agent-health', {
        body: {
          action: 'get_agents',
          agent_data: {
            organization_id: organizationId,
            status: status
          }
        }
      });

      if (error) throw error;
      return data.data;
    },
    enabled: !!user && !!organizationId,
    refetchInterval: 60000 // Refresh every minute
  });
}

// Hook for fetching dashboard metrics
export function useDashboardMetrics(organizationId: string, timeRange: string = '24h') {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['dashboard-metrics', organizationId, timeRange],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');

      const { data, error } = await supabase.functions.invoke('analytics-reports', {
        body: {
          action: 'generate_dashboard_metrics',
          report_data: {
            organization_id: organizationId,
            time_range: timeRange
          }
        }
      });

      if (error) throw error;
      return data.data;
    },
    enabled: !!user && !!organizationId,
    refetchInterval: 30000 // Refresh every 30 seconds
  });
}

// Hook for fetching investigations
export function useInvestigations(organizationId: string, status?: string) {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['investigations', organizationId, status],
    queryFn: async () => {
      if (!user) throw new Error('User not authenticated');

      const { data, error } = await supabase.functions.invoke('investigation-manager', {
        body: {
          action: 'get_investigations',
          investigation_data: {
            organization_id: organizationId,
            status: status
          }
        }
      });

      if (error) throw error;
      return data.data;
    },
    enabled: !!user && !!organizationId
  });
}