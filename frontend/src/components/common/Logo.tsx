import React from 'react';

export interface LogoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  withText?: boolean;
  textClassName?: string;
  subtitleClassName?: string;
  className?: string;
  glow?: boolean;
}

const SIZE_MAP = {
  xs: 24,
  sm: 32,
  md: 40,
  lg: 52,
  xl: 68,
};

export const Logo: React.FC<LogoProps> = ({
  size = 'md',
  withText = false,
  textClassName = '',
  subtitleClassName = '',
  className = '',
  glow = true,
}) => {
  const pixelSize = typeof size === 'number' ? size : SIZE_MAP[size] || 40;

  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      {/* SVG Icon Emblem */}
      <div
        className={`relative flex items-center justify-center shrink-0 transition-transform duration-200 hover:scale-105 ${
          glow ? 'drop-shadow-[0_4px_16px_rgba(14,165,233,0.35)]' : ''
        }`}
        style={{ width: pixelSize, height: pixelSize }}
      >
        <svg
          viewBox="0 0 120 120"
          width="100%"
          height="100%"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-label="Swasthya Records Logo"
        >
          <defs>
            {/* Background Shield Gradient */}
            <linearGradient id="sg-bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0ea5e9" />
              <stop offset="45%" stopColor="#2563eb" />
              <stop offset="100%" stopColor="#1e1b4b" />
            </linearGradient>

            {/* Premium Metallic Border Gradient */}
            <linearGradient id="sg-border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#7dd3fc" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#38bdf8" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#818cf8" stopOpacity="0.2" />
            </linearGradient>

            {/* Medical Cross Gloss Gradient */}
            <linearGradient id="sg-cross-grad" x1="50%" y1="0%" x2="50%" y2="100%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="100%" stopColor="#e0f2fe" />
            </linearGradient>

            {/* ECG Pulse / Logistics Route Gradient */}
            <linearGradient id="sg-pulse-grad" x1="0%" y1="50%" x2="100%" y2="50%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="35%" stopColor="#06b6d4" />
              <stop offset="65%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#34d399" />
            </linearGradient>

            {/* Soft Drop Shadow for Cross */}
            <filter id="sg-cross-shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="3" stdDeviation="3.5" floodColor="#091e42" floodOpacity="0.32" />
            </filter>

            {/* Neon Glow Filter for Pulse */}
            <filter id="sg-pulse-glow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="1.8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Squircle Base with Soft Outer Shadow */}
          <rect
            x="6"
            y="6"
            width="108"
            height="108"
            rx="28"
            fill="url(#sg-bg-grad)"
          />

          {/* Inner Light Bevel Border */}
          <rect
            x="6"
            y="6"
            width="108"
            height="108"
            rx="28"
            fill="none"
            stroke="url(#sg-border-grad)"
            strokeWidth="2.5"
          />

          {/* Telemetry Radar Rings (Subtle Grid Context) */}
          <circle cx="60" cy="60" r="46" fill="none" stroke="#ffffff" strokeOpacity="0.07" strokeDasharray="3 4" />
          <circle cx="60" cy="60" r="32" fill="none" stroke="#ffffff" strokeOpacity="0.05" strokeDasharray="2 3" />

          {/* Medical Cross Geometry (Embossed & Soft-Rounded) */}
          <g filter="url(#sg-cross-shadow)">
            {/* Vertical Bar */}
            <rect
              x="47"
              y="22"
              width="26"
              height="76"
              rx="10"
              fill="url(#sg-cross-grad)"
            />
            {/* Horizontal Bar */}
            <rect
              x="22"
              y="47"
              width="76"
              height="26"
              rx="10"
              fill="url(#sg-cross-grad)"
            />
          </g>

          {/* Orbital Rebalancing Swooshes (Signifying Supply Agility) */}
          <path
            d="M 30 28 C 48 16, 74 18, 92 30"
            stroke="#7dd3fc"
            strokeWidth="2"
            strokeLinecap="round"
            strokeOpacity="0.5"
            fill="none"
          />
          <path
            d="M 90 92 C 72 104, 46 102, 28 90"
            stroke="#34d399"
            strokeWidth="2"
            strokeLinecap="round"
            strokeOpacity="0.5"
            fill="none"
          />

          {/* Vital Lifeline / Supply Chain Telemetry ECG Wave */}
          <path
            d="M 22 60 L 42 60 L 47 60 L 53 38 L 59 78 L 65 48 L 70 64 L 75 60 L 98 60"
            fill="none"
            stroke="url(#sg-pulse-grad)"
            strokeWidth="4.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter="url(#sg-pulse-glow)"
          />

          {/* Telemetry Grid Nodes (Donor, Hub, Recipient) */}
          {/* 1. Donor Source Node (Left) */}
          <circle cx="26" cy="60" r="5" fill="#0284c7" fillOpacity="0.25" />
          <circle cx="26" cy="60" r="3" fill="#38bdf8" />

          {/* 2. Central Peak / Early Warning Radar Node */}
          <circle cx="53" cy="38" r="6" fill="#10b981" fillOpacity="0.3" />
          <circle cx="53" cy="38" r="3.2" fill="#34d399" />

          {/* 3. Recipient Node (Right) */}
          <circle cx="94" cy="60" r="5" fill="#10b981" fillOpacity="0.25" />
          <circle cx="94" cy="60" r="3" fill="#10b981" />
        </svg>
      </div>

      {/* Brand Text (Optional) */}
      {withText && (
        <div className="flex flex-col">
          <span className={`font-extrabold tracking-tight text-slate-900 leading-tight ${textClassName || 'text-base sm:text-lg'}`}>
            Swasthya<span className="text-primary font-black">Records</span>
          </span>
          <span className={`text-[10px] tracking-wider uppercase font-semibold text-slate-500 flex items-center gap-1 ${subtitleClassName}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            HealthGrid AI
          </span>
        </div>
      )}
    </div>
  );
};
