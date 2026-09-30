import React, { useState } from 'react';
import {
  Search,
  Bell,
  User,
  ChevronDown,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { useLanguage, Language } from '../../context/LanguageContext';
import { useAuth, PRESET_USERS } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { UserRole } from '../../types';

interface HeaderProps {
  onOpenSearch: () => void;
  onOpenCopilot: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSearch, onOpenCopilot }) => {
  const { language, setLanguage, t } = useLanguage();
  const { user, switchRole, logout } = useAuth();
  const { notifications, unreadCount, markAllAsRead } = useNotifications();

  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [showNotifMenu, setShowNotifMenu] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-command-700 bg-command-900/95 backdrop-blur-sm">
      <div className="flex h-14 items-center justify-between px-4 sm:px-6">
        {/* Left: Brand */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white font-bold text-sm">
              SR
            </div>
            <div>
              <span className="font-bold tracking-tight text-slate-900 text-sm sm:text-base">
                {t('app.title')}
              </span>
              <p className="hidden md:block text-xs text-slate-500">
                {t('app.subtitle')}
              </p>
            </div>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2">
          {/* Search */}
          <button
            onClick={onOpenSearch}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-command-700 hover:border-command-600 text-slate-500 hover:text-slate-700 text-xs transition-colors"
            title="Search (Ctrl+K)"
          >
            <Search className="w-4 h-4" />
            <span className="hidden md:inline">Search...</span>
            <kbd className="hidden md:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-command-800 border border-command-700 rounded text-slate-500">
              ⌘K
            </kbd>
          </button>

          {/* Language Toggle */}
          <div className="flex items-center rounded-lg border border-command-700 p-0.5 text-xs">
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 rounded-md font-medium transition-all ${
                language === 'en'
                  ? 'bg-primary text-white'
                  : 'text-slate-500 hover:text-slate-200'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('hi')}
              className={`px-2 py-1 rounded-md font-medium transition-all ${
                language === 'hi'
                  ? 'bg-primary text-white'
                  : 'text-slate-500 hover:text-slate-200'
              }`}
            >
              हिन्दी
            </button>
          </div>

          {/* AI Assistant */}
          <button
            onClick={onOpenCopilot}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">AI Assistant</span>
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifMenu(!showNotifMenu);
                setShowRoleMenu(false);
              }}
              className="relative p-2 rounded-lg border border-command-700 hover:border-command-600 text-slate-600 transition-colors"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-risk-critical text-[10px] font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifMenu && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-command-700 bg-command-900 shadow-2xl p-4 z-50">
                <div className="flex items-center justify-between border-b border-command-700 pb-3 mb-3">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-risk-critical" />
                    <h4 className="text-sm font-bold text-slate-800">Notifications</h4>
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-primary hover:text-primary-hover font-medium"
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-72 overflow-y-auto space-y-2">
                  {notifications.length === 0 ? (
                    <p className="text-xs text-slate-500 py-4 text-center">No active alerts</p>
                  ) : (
                    notifications.slice(0, 5).map((n) => (
                      <div
                        key={n.alert_id}
                        className="p-2.5 rounded-lg bg-command-850 border border-command-700 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-700">{n.facility_name}</span>
                          <span className="text-xs font-mono text-risk-critical">
                            {(n.days_until_breach ?? 0) < 1 ? '< 1 day' : `${(n.days_until_breach ?? 0).toFixed(1)}d`}
                          </span>
                        </div>
                        <p className="text-slate-600">{n.recommended_action || n.recommended_next_step || ''}</p>
                        <span className="text-xs text-slate-500">{n.district}, {n.state}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User / Role Switcher */}
          <div className="relative">
            <button
              onClick={() => {
                setShowRoleMenu(!showRoleMenu);
                setShowNotifMenu(false);
              }}
              className="flex items-center gap-2 p-1.5 sm:px-3 sm:py-1.5 rounded-lg border border-command-700 hover:border-command-600 transition-colors"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-command-800 border border-command-700 text-sm">
                {user.avatar || '👤'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-medium text-slate-700 leading-tight">{user.name.split(' ')[0]}</p>
                <p className="text-[11px] text-primary font-mono leading-tight">{user.role}</p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </button>

            {showRoleMenu && (
              <div className="absolute right-0 mt-2 w-60 rounded-xl border border-command-700 bg-command-900 shadow-2xl p-2 z-50">
                <div className="px-3 py-2 border-b border-command-700 mb-1">
                  <p className="text-xs font-semibold text-slate-700">{user.name}</p>
                  <p className="text-xs text-slate-500">{user.region}</p>
                </div>
                <div className="space-y-0.5">
                  <p className="px-3 py-1.5 text-[11px] font-semibold uppercase text-slate-500">Switch Role</p>
                  {(['ADMIN', 'STATE_OPERATOR', 'DISTRICT_OPERATOR'] as UserRole[]).map((r) => (
                    <button
                      key={r}
                      onClick={() => {
                        switchRole(r);
                        setShowRoleMenu(false);
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-between transition-colors ${
                        user.role === r
                          ? 'bg-primary/15 text-primary font-semibold'
                          : 'hover:bg-slate-50 text-slate-600'
                      }`}
                    >
                      <span>{PRESET_USERS[r].name}</span>
                      <span className="text-[11px] font-mono text-slate-500">{r}</span>
                    </button>
                  ))}
                </div>
                <div className="mt-1 pt-1 border-t border-command-700">
                  <button
                    onClick={() => {
                      logout();
                      setShowRoleMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-lg text-xs font-medium text-risk-critical hover:bg-risk-critical/10 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
