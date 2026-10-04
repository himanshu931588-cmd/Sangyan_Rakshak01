import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Download, Check, FileCheck, ShieldAlert } from 'lucide-react';
import { GrievanceDossier } from '../../types';
import { useLanguage } from '../../context/LanguageContext';

interface DossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  dossier: GrievanceDossier | null;
}

export const DossierModal: React.FC<DossierModalProps> = ({
  isOpen,
  onClose,
  dossier,
}) => {
  const { t } = useLanguage();
  const [copied, setCopied] = useState(false);

  if (!isOpen || !dossier) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(dossier.dossierMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownload = () => {
    const blob = new Blob([dossier.dossierMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SEBI_SCORES_Complaint_Dossier_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-3xl bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden my-8"
        >
          {/* Modal Header */}
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 font-sans">
                  {t('modalTitle')}
                </h3>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  Target Portal: {dossier.filingPortal}
                </span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Modal Body */}
          <div className="p-6 space-y-5 max-h-[65vh] overflow-y-auto font-sans">
            {/* Markdown Dossier Preview Card */}
            <div className="bg-zinc-900/90 rounded-xl p-4 border border-zinc-800 font-mono text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed shadow-inner">
              {dossier.dossierMarkdown}
            </div>

            {/* Evidentiary Checklist */}
            {dossier.requiredDocuments.length > 0 && (
              <div className="bg-zinc-900/40 p-4 rounded-xl border border-zinc-800 space-y-2">
                <p className="text-xs font-mono text-cyan-400 uppercase font-semibold flex items-center space-x-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Required Submission Evidence Checklist:</span>
                </p>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-zinc-300 pt-1">
                  {dossier.requiredDocuments.map((doc, idx) => (
                    <li key={idx} className="flex items-center space-x-2">
                      <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Modal Footer Controls */}
          <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/60 flex flex-col sm:flex-row items-center justify-between gap-3">
            {copied ? (
              <span className="text-xs font-mono text-emerald-400 flex items-center space-x-1">
                <Check className="w-4 h-4" />
                <span>{t('copiedToast')}</span>
              </span>
            ) : (
              <span className="text-xs font-mono text-zinc-500">
                Ready for official upload to SEBI SCORES 2.0
              </span>
            )}

            <div className="flex items-center space-x-2.5 w-full sm:w-auto">
              <button
                onClick={handleCopy}
                className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium flex items-center justify-center space-x-2 transition-all border border-zinc-700"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>{t('btnCopy')}</span>
              </button>

              <button
                onClick={handleDownload}
                className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{t('btnDownload')}</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
