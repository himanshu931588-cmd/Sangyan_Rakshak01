import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { MessageSquareText, Image as ImageIcon, Mic, Upload, Sparkles, AlertCircle } from 'lucide-react';
import { InputMode, AppState } from '../../types';
import { useLanguage } from '../../context/LanguageContext';

interface UnifiedIngestionIslandProps {
  appState: AppState;
  onScan: (text: string, file: File | null, mode: InputMode) => void;
  onSeedClick: (seedType: 'scam' | 'ria' | 'dabba') => void;
}

export const UnifiedIngestionIsland: React.FC<UnifiedIngestionIslandProps> = ({
  appState,
  onScan,
  onSeedClick,
}) => {
  const { t } = useLanguage();
  const [mode, setMode] = useState<InputMode>('TEXT');
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Auto-detect entity tags in text input
  const detectedEntities = useMemo(() => {
    const tags: string[] = [];
    if (!textInput) return tags;

    if (textInput.includes('http://') || textInput.includes('https://')) {
      tags.push('URL / Web Domain Detected');
    }
    if (/@([a-zA-Z0-9_]{4,})/.test(textInput)) {
      tags.push('Telegram / Handle Detected');
    }
    if (/([a-zA-Z0-9.\-_]+@[a-zA-Z]{3,})/.test(textInput)) {
      tags.push('UPI Payment ID Detected');
    }
    if (/\b(IN[A-Z0-9]{9,12})\b/i.test(textInput)) {
      tags.push('SEBI Reg Number Detected');
    }
    if (/\d+%\s*(daily|monthly|per day)/i.test(textInput)) {
      tags.push('Guaranteed Return Yield Claim');
    }
    return tags;
  }, [textInput]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() && !selectedFile) return;
    onScan(textInput, selectedFile, mode);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      {/* Glassmorphic Container Card */}
      <div className="backdrop-blur-md bg-zinc-900/70 border border-zinc-800/90 rounded-2xl p-5 shadow-2xl shadow-black/40 space-y-4 transition-all">
        
        {/* Segmented Pill Mode Selector */}
        <div className="grid grid-cols-3 gap-1.5 p-1 bg-zinc-950/80 rounded-xl border border-zinc-800/80">
          <button
            type="button"
            onClick={() => setMode('TEXT')}
            className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-lg text-xs font-medium transition-all ${
              mode === 'TEXT'
                ? 'bg-zinc-800 text-cyan-400 border border-zinc-700 shadow'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
            }`}
          >
            <MessageSquareText className="w-3.5 h-3.5" />
            <span className="truncate">{t('tabText')}</span>
          </button>

          <button
            type="button"
            onClick={() => setMode('OCR')}
            className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-lg text-xs font-medium transition-all ${
              mode === 'OCR'
                ? 'bg-zinc-800 text-cyan-400 border border-zinc-700 shadow'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
            }`}
          >
            <ImageIcon className="w-3.5 h-3.5" />
            <span className="truncate">{t('tabOcr')}</span>
          </button>

          <button
            type="button"
            onClick={() => setMode('AUDIO')}
            className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-lg text-xs font-medium transition-all ${
              mode === 'AUDIO'
                ? 'bg-zinc-800 text-cyan-400 border border-zinc-700 shadow'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
            }`}
          >
            <Mic className="w-3.5 h-3.5" />
            <span className="truncate">{t('tabAudio')}</span>
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          {mode === 'TEXT' ? (
            <div className="relative">
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder={t('placeholderText')}
                rows={3}
                className="w-full bg-zinc-950/90 border border-zinc-800 rounded-xl p-3.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all resize-none font-sans"
              />
            </div>
          ) : (
            <div className="border-2 border-dashed border-zinc-800 hover:border-cyan-500/50 rounded-xl p-6 bg-zinc-950/50 text-center transition-all cursor-pointer relative">
              <input
                type="file"
                accept={mode === 'OCR' ? 'image/*' : 'audio/*'}
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center justify-center space-y-2 text-zinc-400">
                <Upload className="w-7 h-7 text-cyan-400 mb-1" />
                <p className="text-xs font-medium">
                  {selectedFile
                    ? `Selected File: ${selectedFile.name}`
                    : mode === 'OCR'
                    ? t('placeholderOcr')
                    : t('placeholderAudio')}
                </p>
                <p className="text-[11px] text-zinc-600 font-mono">
                  {mode === 'OCR' ? 'Supports JPG, PNG, WEBP' : 'Supports WAV, MP3, M4A'}
                </p>
              </div>
            </div>
          )}

          {/* Auto-detected Entity Badges */}
          {detectedEntities.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {detectedEntities.map((tag, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-300"
                >
                  <Sparkles className="w-2.5 h-2.5" />
                  <span>{tag}</span>
                </span>
              ))}
            </div>
          )}

          {/* Tactile Spring Scan Action Button */}
          <motion.button
            whileTap={{ scale: 0.97 }}
            type="submit"
            disabled={appState === 'SCANNING'}
            className={`w-full py-3.5 px-6 rounded-xl font-medium text-sm flex items-center justify-center space-x-2 transition-all shadow-lg ${
              appState === 'SCANNING'
                ? 'bg-zinc-800 text-zinc-500 border border-zinc-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white border border-cyan-400/30 shadow-cyan-500/20 active:shadow-none'
            }`}
          >
            {appState === 'SCANNING' ? (
              <>
                <div className="w-4 h-4 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
                <span>{t('btnScanning')}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-200" />
                <span className="tracking-wide font-semibold">{t('btnScan')}</span>
              </>
            )}
          </motion.button>
        </form>

        {/* Benchmark Demo Seed Badges */}
        <div className="pt-2 border-t border-zinc-800/60 space-y-2">
          <div className="flex items-center space-x-1 text-[11px] font-mono text-zinc-400">
            <AlertCircle className="w-3 h-3 text-cyan-400" />
            <span>{t('demoSeedsTitle')}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => {
                setTextInput('Join @RoyalForex_VIP_Signals for 35% daily return guarantee! Pay to scammer10x@ybl.');
                onSeedClick('scam');
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-mono bg-rose-500/10 border border-rose-500/30 text-rose-300 hover:bg-rose-500/20 transition-all text-left"
            >
              🚨 1. {t('demoSeed1')}
            </button>

            <button
              type="button"
              onClick={() => {
                setTextInput('Checking SEBI Registered RIA INA000012345 Apex Capital Wealth Advisors.');
                onSeedClick('ria');
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-mono bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 transition-all text-left"
            >
              ✅ 2. {t('demoSeed2')}
            </button>

            <button
              type="button"
              onClick={() => {
                setTextInput('Trade off-exchange on Nifty Dabba Kings portal without demat account.');
                onSeedClick('dabba');
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-mono bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 transition-all text-left"
            >
              ⚡ 3. {t('demoSeed3')}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
