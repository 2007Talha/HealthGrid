import React, { createContext, useContext, useState, useEffect } from 'react';
import { alertsApi } from '../api/alerts';
import { EarlyWarningAlert } from '../types';

interface NotificationContextType {
  notifications: EarlyWarningAlert[];
  unreadCount: number;
  markAllAsRead: () => void;
  refreshNotifications: () => Promise<void>;
  isLoading: boolean;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<EarlyWarningAlert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const refreshNotifications = async () => {
    try {
      setIsLoading(true);
      const res = await alertsApi.getCriticalAlerts();
      const items = res.alerts || [];
      setNotifications(items);
      setUnreadCount(items.length);
    } catch {
      // Ignored in offline/startup mode
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshNotifications();
    const interval = setInterval(refreshNotifications, 30000); // 30s polling
    return () => clearInterval(interval);
  }, []);

  const markAllAsRead = () => {
    setUnreadCount(0);
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        markAllAsRead,
        refreshNotifications,
        isLoading
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
