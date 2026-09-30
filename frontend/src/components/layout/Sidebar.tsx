import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  Pill,
  Building2,
  TrendingUp,
  RefreshCw,
  Flame,
  Bot,
  Activity,
  Info,
  PlayCircle
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import { useNotifications } from '../../context/NotificationContext';

export type NavRoute =
  | 'dashboard'
  | 'alerts'
  | 'medicines'
  | 'facilities'
  | 'forecasts'
  | 'redistribution'
  | 'emergencies'
  | 'copilot'
  | 'demo'
  | 'system'
  | 'about';

interface SidebarProps {
  currentRoute: NavRoute;
  onNavigate: (route: NavRoute) => void;
}

interface NavSection {
  label: string;
  items: Array<{
    id: NavRoute;
    labelKey: string;
    icon: React.FC<{ className?: string }>;
    badge?: number;
  }>;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRoute, onNavigate }) => {
  const { t } = useLanguage();
  const { unreadCount } = useNotifications();

  const sections: NavSection[] = [
    {
      label: 'Overview',
      items: [
        { id: 'dashboard', labelKey: 'nav.dashboard', icon: LayoutDashboard },
      ],
    },
    {
      label: 'Monitoring',
      items: [
        { id: 'alerts', labelKey: 'nav.alerts', icon: AlertTriangle, badge: unreadCount || undefined },
        { id: 'medicines', labelKey: 'nav.medicines', icon: Pill },
        { id: 'facilities', labelKey: 'nav.facilities', icon: Building2 },
      ],
    },
    {
      label: 'Intelligence',
      items: [
        { id: 'forecasts', labelKey: 'nav.forecasts', icon: TrendingUp },
        { id: 'redistribution', labelKey: 'nav.redistribution', icon: RefreshCw },
        { id: 'emergencies', labelKey: 'nav.emergencies', icon: Flame },
      ],
    },
    {
      label: 'Tools',
      items: [
        { id: 'copilot', labelKey: 'nav.copilot', icon: Bot },
        { id: 'demo', labelKey: 'nav.demo', icon: PlayCircle },
      ],
    },
    {
      label: 'Settings',
      items: [
        { id: 'system', labelKey: 'nav.system', icon: Activity },
        { id: 'about', labelKey: 'nav.about', icon: Info },
      ],
    },
  ];

  return (
    <aside className="w-56 shrink-0 border-r border-command-700 bg-command-950 flex flex-col p-3 hidden md:flex overflow-y-auto">
      <nav className="space-y-5 flex-1">
        {sections.map((section) => (
          <div key={section.label}>
            <p className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              {section.label}
            </p>
            <div className="mt-1 space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentRoute === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-[13px] font-medium transition-colors ${
                      isActive
                        ? 'bg-primary/15 text-primary font-semibold'
                        : 'text-slate-500 hover:text-slate-800 hover:bg-command-800'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 ${
                          isActive ? 'text-primary' : 'text-slate-500'
                        }`}
                      />
                      <span>{t(item.labelKey)}</span>
                    </div>

                    {item.badge !== undefined && item.badge > 0 && (
                      <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded-full bg-risk-critical text-slate-900">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
};
