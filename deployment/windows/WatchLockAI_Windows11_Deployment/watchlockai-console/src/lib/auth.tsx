import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase, UserProfile } from './supabase';
import { apiService } from './api';

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<any>;
  signUp: (email: string, password: string, organizationId: string) => Promise<any>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user on mount (one-time check)
  useEffect(() => {
    async function loadUser() {
      setLoading(true);
      try {
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        setSession(currentSession);
        setUser(currentSession?.user || null);
        
        if (currentSession?.user) {
          await loadUserProfile(currentSession.user.id);
        }
      } catch (error) {
        console.error('Error loading user:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadUser();

    // Set up auth listener - KEEP SIMPLE, avoid any async operations in callback
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, currentSession) => {
        // NEVER use any async operations in callback
        setSession(currentSession);
        setUser(currentSession?.user || null);
        
        // Use setTimeout to avoid async operations in callback
        if (currentSession?.user) {
          setTimeout(() => {
            loadUserProfile(currentSession.user.id);
          }, 0);
        } else {
          setProfile(null);
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  async function loadUserProfile(userId: string) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .maybeSingle();

      if (error) {
        console.error('Error loading profile:', error);
        return;
      }

      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }

  async function signIn(email: string, password: string) {
    // Check for demo credentials first to enable testing
    if ((email === 'demo@demo.com' && password === 'demo123') || 
        (email === 'admin@demo.com' && password === 'admin123')) {
      
      // Create a demo user object for testing
      const demoUser = {
        id: 'demo-user-123',
        email: email,
        aud: 'authenticated',
        role: 'authenticated',
        email_confirmed_at: new Date().toISOString(),
        last_sign_in_at: new Date().toISOString(),
        app_metadata: {},
        user_metadata: { full_name: email.includes('admin') ? 'System Administrator' : 'Demo User' },
        identities: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      } as any;

      const demoProfile: UserProfile = {
        id: 'demo-user-123',
        email: email,
        full_name: email.includes('admin') ? 'System Administrator' : 'Demo User',
        role: 'admin' as const,
        organization_id: 'demo-org-123',
        permissions: ['read', 'write', 'admin', 'manage_users', 'manage_agents', 'manage_policies'],
        avatar_url: null,
        last_login_at: new Date().toISOString(),
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      setUser(demoUser);
      setProfile(demoProfile);
      setSession({
        access_token: 'demo-token',
        refresh_token: 'demo-refresh',
        expires_in: 3600,
        token_type: 'bearer',
        user: demoUser
      } as any);
      
      return { user: demoUser, session: null };
    }

    // Try real Supabase authentication
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) throw error;
      return data;
    } catch (error: any) {
      // If Supabase auth fails and it's not demo credentials, show error
      throw new Error('Invalid login credentials. Use demo@demo.com / demo123 for testing.');
    }
  }

  async function signUp(email: string, password: string, organizationId: string) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.protocol}//${window.location.host}/auth/callback`,
        data: {
          organization_id: organizationId
        }
      }
    });

    if (error) throw error;
    return data;
  }

  async function signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    
    setUser(null);
    setProfile(null);
    setSession(null);
  }

  async function refreshProfile() {
    if (user) {
      await loadUserProfile(user.id);
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      profile,
      session,
      loading,
      signIn,
      signUp,
      signOut,
      refreshProfile
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}