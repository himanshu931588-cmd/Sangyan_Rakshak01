import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, AlertTriangle, FileText, CheckCircle, XCircle } from 'lucide-react';
import { VerificationResult } from '../../types';
import { useLanguage } from '../../context/LanguageContext';

interface VerdictSurfaceProps {
  result: VerificationResult;
  onGenerateDossier: () => void;
}

export const VerdictSurface: React.FC<VerdictSurfaceProps> = ({
  result,
  onGenerateDossier,
}) => {
  const { t } = useLanguage();
  const { verdict, riskScore, flags, analysisVernacular, matchedRegInfo, deceptionMetrics } = result;

  const getVerdictStyle = () => {
    switch (verdict) {
      case 'CRITICAL_FRAUD':
      case 'HIGH_RISK':
        return {
          bg: 'bg-rose-500/10 border-rose-500/40 text-rose-400',
          badgeBg: 'bg-rose-500 text-white shadow-lg shadow-rose-500/30',
          icon: ShieldAlert,
          title: 'खतरा / CRITICAL FRAUD RISK',
        };
      case 'SUSPICIOUS':
        return {
          bg: 'bg-amber-500/10 border-amber-500/40 text-amber-400',
          badgeBg: 'bg-amber-500 text-zinc-950 shadow-lg shadow-amber-500/30',
          icon: AlertTriangle,
          title: 'संदिग्ध / SUSPICIOUS OFFER',
        };
      case 'SAFE':
      default:
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400',
          badgeBg: 'bg-emerald-500 text-zinc-950 shadow-lg shadow-emerald-500/30',
          icon: ShieldCheck,
          title: 'सुरक्षित / VERIFIED SAFE',
        };
    }
  };

  const style = getVerdictStyle();
  const VerdictIcon = style.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="w-full max-w-2xl mx-auto space-y-4"
    >
      {/* Primary Verdict Glassmorphic Surface */}
      <div className={`backdrop-blur-md rounded-2xl p-6 border ${style.bg} space-y-5 shadow-2xl`}>
        
        {/* Top Header & Verdict Badge */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-zinc-800/60">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-xl ${style.badgeBg}`}>
              <VerdictIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight text-zinc-100 font-sans">
                {style.title}
              </h2>
              <p className="text-xs font-mono text-zinc-400">
                Risk Probability Index: {(riskScore * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onGenerateDossier}
            className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 active:shadow-none transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>{t('btnGenerateDossier')}</span>
          </motion.button>
        </div>

        {/* Signal Breakdown Progress Bars */}
        <div className="space-y-3 pt-1">
          <h3 className="text-xs font-mono tracking-wider text-zinc-400 uppercase">
            {t('verdictTitle')}
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Unrealistic Yield Risk Bar */}
            <div className="bg-zinc-950/70 p-3 rounded-xl border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-400 font-mono text-[11px]">{t('yieldRiskLabel')}</span>
                <span className="font-mono text-rose-400 font-semibold">{deceptionMetrics.yieldRisk}%</span>
              </div>
              <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-rose-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${deceptionMetrics.yieldRisk}%` }}
                />
              </div>
            </div>

            {/* FOMO Index Bar */}
            <div className="bg-zinc-950/70 p-3 rounded-xl border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-400 font-mono text-[11px]">{t('fomoRiskLabel')}</span>
                <span className="font-mono text-amber-400 font-semibold">{deceptionMetrics.fomoRisk}%</span>
              </div>
              <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-amber-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${deceptionMetrics.fomoRisk}%` }}
                />
              </div>
            </div>

            {/* SEBI Registry Match Bar */}
            <div className="bg-zinc-950/70 p-3 rounded-xl border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-400 font-mono text-[11px]">{t('registryMatchLabel')}</span>
                <span className="font-mono text-emerald-400 font-semibold">{deceptionMetrics.registryMatch}%</span>
              </div>
              <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${deceptionMetrics.registryMatch}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* SEBI Entity Verification Card (if matched) */}
        {matchedRegInfo && (
          <div className="bg-zinc-950/90 rounded-xl p-4 border border-emerald-500/30 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-emerald-400 flex items-center space-x-1.5">
                <CheckCircle className="w-4 h-4" />
                <span>{t('matchedEntityTitle')}</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                {matchedRegInfo.status === 'ACTIVE' ? t('entityActive') : t('entitySuspended')}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <p className="text-zinc-400 text-[11px]">Entity Name:</p>
                <p className="font-semibold text-zinc-100">{matchedRegInfo.entity_name}</p>
              </div>
              <div>
                <p className="text-zinc-400 text-[11px]">Registration No:</p>
                <p className="font-mono text-cyan-400 font-semibold">{matchedRegInfo.reg_number}</p>
              </div>
            </div>
          </div>
        )}

        {/* Vernacular AI Explanation Summary */}
        <div className="bg-zinc-950/80 rounded-xl p-4 border border-zinc-800 text-xs text-zinc-200 leading-relaxed font-sans space-y-2">
          <div className="whitespace-pre-line">{analysisVernacular}</div>
        </div>

        {/* Risk Markers & Flags */}
        {flags.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
              Audit Risk Markers:
            </p>
            <ul className="space-y-1">
              {flags.map((flag, i) => (
                <li key={i} className="text-xs text-zinc-300 flex items-start space-x-2">
                  <span className="text-rose-400 font-bold mt-0.5">•</span>
                  <span>{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

      </div>
    </motion.div>
  );
};
