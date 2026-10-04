import React, { createContext, useContext, useState } from 'react';
import { Language } from '../types';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    appTitle: 'Sangyan Rakshak',
    appSubtitle: 'Investor Scam Shield & SEBI Verification Engine',
    sebiLive: 'SEBI Registry Online',
    lowPowerMode: 'Low-Power WebGL',
    normalMode: '3D WebGL Engine',
    tabText: 'Forward / Message Text',
    tabOcr: 'Screenshot OCR',
    tabAudio: 'Vernacular Voice Note',
    placeholderText: 'Paste suspicious Telegram offer, WhatsApp message, SEBI registration claim, or UPI payment handle...',
    placeholderOcr: 'Drop or select screenshot image (.jpg, .png) for instant OCR analysis...',
    placeholderAudio: 'Drop or select voice note recording (.wav, .mp3) for audio scam analysis...',
    btnScan: 'Analyze Payload Security',
    btnScanning: 'Scanning Registries & AI Heuristics...',
    demoSeedsTitle: 'One-Click Benchmark Demos:',
    demoSeed1: 'Telegram 35% Daily Return',
    demoSeed2: 'SEBI Registered RIA Check',
    demoSeed3: 'Dabba Trading Clone App',
    verdictTitle: 'Verification Signal Analysis',
    yieldRiskLabel: 'Unrealistic Yield Risk',
    fomoRiskLabel: 'FOMO & Pressure Index',
    registryMatchLabel: 'SEBI Registry Authentication',
    matchedEntityTitle: 'SEBI License Verification',
    entityActive: 'ACTIVE REGISTRATION',
    entitySuspended: 'SUSPENDED REGISTRATION',
    btnGenerateDossier: 'Generate 1-Click SEBI SCORES Dossier',
    modalTitle: 'Official SEBI SCORES Complaint Dossier',
    btnCopy: 'Copy Markdown',
    btnDownload: 'Download Dossier (.md)',
    copiedToast: 'Dossier copied to clipboard!',
    closeModal: 'Close',
  },
  hi: {
    appTitle: 'संज्ञान रक्षक',
    appSubtitle: 'निवेशक स्कैम-शील्ड एवं सेबी (SEBI) सत्यापन इंजन',
    sebiLive: 'SEBI रजिस्ट्री लाइव',
    lowPowerMode: 'लो-पावर 2D मोड',
    normalMode: '3D वेब-जीएल इंजन',
    tabText: 'फॉरवर्ड संदेश / टेक्स्ट',
    tabOcr: 'स्क्रीनशॉट OCR',
    tabAudio: 'वॉइस मैसेज ऑडियो',
    placeholderText: 'संदिग्ध टेलीग्राम ऑफर, व्हाट्सएप संदेश, SEBI रजिस्ट्रेशन नंबर या UPI पेमेंट हैंडल पेस्ट करें...',
    placeholderOcr: 'त्वरित OCR विश्लेषण के लिए स्क्रीनशॉट (.jpg, .png) ड्रॉप या सिलेक्ट करें...',
    placeholderAudio: 'ऑडियो स्कैम विश्लेषण के लिए वॉइस रिकॉर्डिंग (.wav, .mp3) चुनें...',
    btnScan: 'पेलोड सुरक्षा जांचें',
    btnScanning: 'स्कैनिंग एवं AI विश्लेषक जारी...',
    demoSeedsTitle: 'वन-क्लिक परीक्षण उदाहरण:',
    demoSeed1: 'टेलीग्राम 35% दैनिक रिटर्न',
    demoSeed2: 'SEBI पंजीकृत RIA जांच',
    demoSeed3: 'डब्बा ट्रेडिंग क्लोन ऐप',
    verdictTitle: 'सत्यापन सिग्नल विश्लेषण',
    yieldRiskLabel: 'अवास्तविक रिटर्न जोखिम',
    fomoRiskLabel: 'FOMO दबाव सूचकांक',
    registryMatchLabel: 'SEBI रजिस्ट्री सत्यापन',
    matchedEntityTitle: 'SEBI लाइसेंस प्रमाणन',
    entityActive: 'सक्रिय पंजीकरण (ACTIVE)',
    entitySuspended: 'निलंबित (SUSPENDED)',
    btnGenerateDossier: '1-क्लिक SEBI SCORES शिकायत ड्राफ्ट बनाएं',
    modalTitle: 'आधिकारिक SEBI SCORES शिकायत डोसीयर',
    btnCopy: 'कॉपी करें (Markdown)',
    btnDownload: 'डाउनलोड करें (.md)',
    copiedToast: 'शिकायत ड्राफ्ट क्लिपबोर्ड में कॉपी हो गया!',
    closeModal: 'बंद करें',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('hi');

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
