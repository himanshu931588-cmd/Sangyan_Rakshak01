import React from 'react';
import { ShieldCheck, Cpu, Globe, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface NavbarProps {
  lowPowerMode: boolean;
  setLowPowerMode: (val: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ lowPowerMode, setLowPowerMode }) => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40 px-4 md:px-8 py-3.5 flex items-center justify-between transition-colors">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400 shadow-lg shadow-cyan-500/10">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-tight text-zinc-100 font-sans">
              {t('appTitle')}
            </h1>
            <span className="hidden sm:inline-flex items-center space-x-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <CheckCircle2 className="w-3 h-3" />
              <span>{t('sebiLive')}</span>
            </span>
          </div>
          <p className="text-xs text-zinc-400 hidden md:block">
            {t('appSubtitle')}
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Low Power Mode Toggle */}
        <button
          onClick={() => setLowPowerMode(!lowPowerMode)}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
            lowPowerMode
              ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
              : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'
          }`}
          title="Toggle 3D WebGL vs 2D SVG rendering"
        >
          <Cpu className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">
            {lowPowerMode ? t('lowPowerMode') : t('normalMode')}
          </span>
        </button>

        {/* Language Selector Toggle */}
        <button
          onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-zinc-800 bg-zinc-900/90 text-cyan-400 hover:border-cyan-500/40 hover:bg-zinc-800 transition-all active:scale-95"
        >
          <Globe className="w-3.5 h-3.5" />
          <span className="font-mono tracking-wider">
            {language === 'en' ? 'ENGLISH' : 'हिंदी'}
          </span>
        </button>
      </div>
    </header>
  );
};
