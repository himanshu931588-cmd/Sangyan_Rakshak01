export type AppState = 'IDLE' | 'SCANNING' | 'VERIFIED' | 'SUSPICIOUS' | 'CRITICAL_FRAUD';

export type InputMode = 'TEXT' | 'OCR' | 'AUDIO';

export type Language = 'en' | 'hi';

export interface MatchedRegInfo {
  reg_number: string;
  entity_name: string;
  category: string;
  status: string;
  valid_until?: string | null;
  complaint_count: number;
}

export interface DeceptionMetrics {
  yieldRisk: number; // 0 - 100
  fomoRisk: number;  // 0 - 100
  registryMatch: number; // 0 - 100
}

export interface VerificationResult {
  verdict: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK' | 'CRITICAL_FRAUD';
  riskScore: number;
  flags: string[];
  analysisVernacular: string;
  matchedRegInfo: MatchedRegInfo | null;
  extractedText?: string;
  extractedUpi?: string;
  extractedRegNumber?: string;
  deceptionMetrics: DeceptionMetrics;
}

export interface GrievanceDossier {
  dossierMarkdown: string;
  filingPortal: 'SEBI_SCORES' | 'CYBERCRIME_PORTAL';
  requiredDocuments: string[];
}
