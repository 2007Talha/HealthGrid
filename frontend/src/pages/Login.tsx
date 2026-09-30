import React, { useState } from 'react';
import { Shield, ArrowRight, Activity, Database, CheckCircle2 } from 'lucide-react';
import { Logo } from '../components/common/Logo';
import { useAuth, PRESET_USERS } from '../context/AuthContext';
import { UserRole } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const Login: React.FC<{ onLoginSuccess: () => void }> = ({ onLoginSuccess }) => {
  const { login } = useAuth();
  const { t } = useLanguage();
  const [selectedRole, setSelectedRole] = useState<UserRole>('ADMIN');

  const handleSignIn = () => {
    login(selectedRole);
    onLoginSuccess();
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gradient-to-b from-command-950 via-command-900 to-command-950">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-command-900/90 shadow-2xl p-8 space-y-6 backdrop-blur-xl">
        {/* Brand Header */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <Logo size={68} glow />
          </div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
            {t('app.title')}
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            National Healthcare Resource & Supply-Chain Resilience Command Center
          </p>
        </div>

        {/* Demo Roles Card Selector */}
        <div className="space-y-3 pt-2">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
            Select Operational Authorization Role
          </label>

          {(['ADMIN', 'STATE_OPERATOR', 'DISTRICT_OPERATOR'] as UserRole[]).map((r) => {
            const user = PRESET_USERS[r];
            const isSelected = selectedRole === r;

            return (
              <div
                key={r}
                onClick={() => setSelectedRole(r)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                  isSelected
                    ? 'border-blue-500/80 bg-blue-50 text-slate-900 shadow-md shadow-blue-100'
                    : 'border-slate-200 bg-command-950/60 text-slate-600 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{user.avatar}</span>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800">{user.name}</h4>
                    <p className="text-[11px] text-slate-500">{user.region}</p>
                  </div>
                </div>
                {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
              </div>
            );
          })}
        </div>

        {/* Sign In Button */}
        <button
          onClick={handleSignIn}
          className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-extrabold flex items-center justify-center gap-2 shadow-lg shadow-blue-200/50 transition-all active:scale-98"
        >
          <span>Access Command Center</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        {/* Footnote */}
        <div className="pt-2 text-center text-[11px] text-slate-500 space-y-1">
          <p>Hackathon Track 3: Smart Health & Supply Chain Resilience</p>
          <p className="text-slate-600">Federated official MoHFW & HMIS data foundation</p>
        </div>
      </div>
    </div>
  );
};
