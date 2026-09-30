import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, UserRole } from '../types';

interface AuthContextType {
  user: UserProfile;
  login: (role: UserRole, region?: string) => void;
  logout: () => void;
  switchRole: (role: UserRole, region?: string) => void;
  isAuthenticated: boolean;
}

export const PRESET_USERS: Record<UserRole, UserProfile> = {
  ADMIN: {
    id: 'usr-admin-national',
    name: 'Dr. Rajesh Sharma',
    role: 'ADMIN',
    region: 'National Health Command',
    avatar: '👨‍💼'
  },
  STATE_OPERATOR: {
    id: 'usr-state-bihar',
    name: 'Pooja Verma (State Director)',
    role: 'STATE_OPERATOR',
    region: 'Bihar (IN-BR)',
    avatar: '👩‍⚕️'
  },
  DISTRICT_OPERATOR: {
    id: 'usr-dist-patna',
    name: 'Dr. Amit Sinha (District Nodal)',
    role: 'DISTRICT_OPERATOR',
    region: 'Patna District',
    avatar: '👨‍⚕️'
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return localStorage.getItem('swasthya_authenticated') === 'true';
  });

  const [user, setUser] = useState<UserProfile>(() => {
    const savedRole = (localStorage.getItem('swasthya_user_role') as UserRole) || 'ADMIN';
    return PRESET_USERS[savedRole] || PRESET_USERS.ADMIN;
  });

  const login = (role: UserRole, region?: string) => {
    const base = PRESET_USERS[role];
    const updated = region ? { ...base, region } : base;
    setUser(updated);
    setIsAuthenticated(true);
    localStorage.setItem('swasthya_authenticated', 'true');
    localStorage.setItem('swasthya_user_role', role);
    localStorage.setItem('swasthya_auth_token', `swasthya-${role.toLowerCase()}-token`);
    localStorage.setItem('swasthya_user_id', updated.id);
    localStorage.setItem('swasthya_user_region', updated.region || '');
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('swasthya_authenticated');
    localStorage.removeItem('swasthya_auth_token');
    localStorage.removeItem('swasthya_user_role');
    localStorage.removeItem('swasthya_user_id');
    localStorage.removeItem('swasthya_user_region');
  };

  const switchRole = (role: UserRole, region?: string) => {
    login(role, region);
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };
    window.addEventListener('swasthya_unauthorized', handleUnauthorized);
    return () => window.removeEventListener('swasthya_unauthorized', handleUnauthorized);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, switchRole, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
