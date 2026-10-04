import { VerificationResult, GrievanceDossier, Language } from '../types';
import { runSyntheticScan, generateSyntheticDossier } from './mockEngine';

const API_BASE = '/api/v1';

export async function verifyText(
  text: string,
  language: Language
): Promise<VerificationResult> {
  try {
    const res = await fetch(`${API_BASE}/verify/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    return transformBackendResponse(data);
  } catch (err) {
    console.warn('Backend API unreachable. Falling back to synthetic scan engine.', err);
    return runSyntheticScan(text, 'TEXT', language);
  }
}

export async function verifyMedia(
  file: File,
  language: Language
): Promise<VerificationResult> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    const res = await fetch(`${API_BASE}/verify/media`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    return transformBackendResponse(data);
  } catch (err) {
    console.warn('Backend API unreachable for media. Falling back to synthetic scan engine.', err);
    return runSyntheticScan(`Media scan of file: ${file.name}`, 'OCR', language);
  }
}

export async function generateGrievanceDossier(
  incidentSummary: string,
  amount: number,
  scammerDetails: Record<string, any>
): Promise<GrievanceDossier> {
  try {
    const res = await fetch(`${API_BASE}/grievance/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_summary: incidentSummary,
        amount: amount,
        scammer_details: scammerDetails,
      }),
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    return {
      dossierMarkdown: data.dossier_markdown,
      filingPortal: data.filing_portal,
      requiredDocuments: data.required_documents || [],
    };
  } catch (err) {
    console.warn('Backend API unreachable for dossier. Falling back to synthetic dossier engine.', err);
    return generateSyntheticDossier(incidentSummary, amount, scammerDetails);
  }
}

function transformBackendResponse(data: any): VerificationResult {
  const riskScore = data.risk_score || 0.0;
  let verdict: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK' | 'CRITICAL_FRAUD' = data.verdict || 'SAFE';

  // Compute deception metrics from risk score and flags
  const yieldRisk = Math.min(Math.round(riskScore * 100), 99);
  const fomoRisk = data.flags && data.flags.length > 1 ? Math.min(Math.round(riskScore * 90) + 10, 95) : 15;
  const registryMatch = data.matched_reg_info ? 100 : 0;

  return {
    verdict,
    riskScore,
    flags: data.flags || [],
    analysisVernacular: data.analysis_vernacular || '',
    matchedRegInfo: data.matched_reg_info || null,
    extractedText: data.extracted_text,
    extractedUpi: data.extracted_upi,
    extractedRegNumber: data.extracted_reg_number,
    deceptionMetrics: {
      yieldRisk,
      fomoRisk,
      registryMatch,
    },
  };
}
