import React, { useState } from 'react';
import { AppState, InputMode, VerificationResult, GrievanceDossier } from './types';
import { useLanguage } from './context/LanguageContext';
import { Navbar } from './components/interaction/Navbar';
import { SecurityCore } from './components/canvas/SecurityCore';
import { UnifiedIngestionIsland } from './components/interaction/UnifiedIngestionIsland';
import { VerdictSurface } from './components/interaction/VerdictSurface';
import { DossierModal } from './components/interaction/DossierModal';
import { verifyText, verifyMedia, generateGrievanceDossier } from './services/api';
import { runSyntheticScan } from './services/mockEngine';

export function App() {
  const { language } = useLanguage();
  const [appState, setAppState] = useState<AppState>('IDLE');
  const [lowPowerMode, setLowPowerMode] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<VerificationResult | null>(null);
  const [dossier, setDossier] = useState<GrievanceDossier | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleScan = async (text: string, file: File | null, mode: InputMode) => {
    setAppState('SCANNING');
    setScanResult(null);

    let result: VerificationResult;

    if (file) {
      result = await verifyMedia(file, language);
    } else {
      result = await verifyText(text, language);
    }

    setScanResult(result);

    // Map backend verdict to 3D State Machine
    if (result.verdict === 'CRITICAL_FRAUD' || result.verdict === 'HIGH_RISK') {
      setAppState('CRITICAL_FRAUD');
    } else if (result.verdict === 'SUSPICIOUS') {
      setAppState('SUSPICIOUS');
    } else {
      setAppState('VERIFIED');
    }
  };

  const handleSeedClick = async (seedType: 'scam' | 'ria' | 'dabba') => {
    setAppState('SCANNING');
    setScanResult(null);

    let sampleText = '';
    if (seedType === 'scam') {
      sampleText = 'Join @RoyalForex_VIP_Signals for 35% daily return guarantee! Pay to scammer10x@ybl.';
    } else if (seedType === 'ria') {
      sampleText = 'Checking SEBI Registered RIA INA000012345 Apex Capital Wealth Advisors.';
    } else {
      sampleText = 'Trade off-exchange on Nifty Dabba Kings portal without demat account.';
    }

    const result = await runSyntheticScan(sampleText, 'TEXT', language);
    setScanResult(result);

    if (result.verdict === 'CRITICAL_FRAUD' || result.verdict === 'HIGH_RISK') {
      setAppState('CRITICAL_FRAUD');
    } else if (result.verdict === 'SUSPICIOUS') {
      setAppState('SUSPICIOUS');
    } else {
      setAppState('VERIFIED');
    }
  };

  const handleGenerateDossier = async () => {
    if (!scanResult) return;

    const summary = scanResult.analysisVernacular || 'Investment advisory fraud incident report.';
    const amount = 250000.0;
    const scammerDetails = {
      reg_number: scanResult.extractedRegNumber || (scanResult.matchedRegInfo ? scanResult.matchedRegInfo.reg_number : undefined),
      intermediary_name: scanResult.matchedRegInfo ? scanResult.matchedRegInfo.entity_name : 'Unregistered Fraud Entity',
      channel_handle: scanResult.flags.find(f => f.includes('@')) || '@RoyalForex_VIP_Signals',
      upi_id: scanResult.extractedUpi || 'scammer10x@ybl',
    };

    const dossierData = await generateGrievanceDossier(summary, amount, scammerDetails);
    setDossier(dossierData);
    setIsModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col justify-between selection:bg-cyan-500/20 selection:text-cyan-300">
      {/* Sticky Header */}
      <Navbar lowPowerMode={lowPowerMode} setLowPowerMode={setLowPowerMode} />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 md:py-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left / Center 3D Security Core Canvas Anchor */}
        <div className="lg:col-span-5 h-[340px] sm:h-[420px] lg:h-[500px] w-full relative flex items-center justify-center rounded-3xl bg-gradient-to-b from-zinc-900/40 to-zinc-950/80 border border-zinc-800/60 shadow-2xl overflow-hidden group">
          <SecurityCore appState={appState} lowPowerMode={lowPowerMode} />
          
          {/* Subtle State Overlay Badge */}
          <div className="absolute top-4 left-4 z-10 px-3 py-1 rounded-full bg-zinc-950/80 border border-zinc-800 text-[11px] font-mono tracking-wider text-zinc-400 backdrop-blur-md">
            CORE_STATE: <span className="text-cyan-400 font-bold">{appState}</span>
          </div>
        </div>

        {/* Right Interaction & Ingestion Island Surface */}
        <div className="lg:col-span-7 space-y-6">
          <UnifiedIngestionIsland
            appState={appState}
            onScan={handleScan}
            onSeedClick={handleSeedClick}
          />

          {/* Verdict Reveal Surface */}
          {scanResult && (
            <VerdictSurface
              result={scanResult}
              onGenerateDossier={handleGenerateDossier}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-zinc-900 py-4 px-6 text-center text-xs font-mono text-zinc-600">
        Sangyan Rakshak — SEBI Regulatory Verification & Multimodal Scam-Shield Engine © 2026
      </footer>

      {/* SEBI SCORES Dossier Modal */}
      <DossierModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        dossier={dossier}
      />
    </div>
  );
}

export default App;
