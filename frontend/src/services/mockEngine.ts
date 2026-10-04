import { VerificationResult, GrievanceDossier } from '../types';

export async function runSyntheticScan(
  inputText: string,
  mode: 'TEXT' | 'OCR' | 'AUDIO',
  language: 'en' | 'hi'
): Promise<VerificationResult> {
  // Simulate network & OCR latency (1.2s)
  await new Promise((resolve) => setTimeout(resolve, 1200));

  const textLower = inputText.toLowerCase();

  // Seed Case 1: Telegram 35% Daily Return / Scam
  if (
    textLower.includes('35%') ||
    textLower.includes('daily return') ||
    textLower.includes('royalforex') ||
    textLower.includes('double money')
  ) {
    return {
      verdict: 'CRITICAL_FRAUD',
      riskScore: 0.98,
      flags: [
        language === 'hi'
          ? 'CRITICAL: ब्लैकलिस्टेड स्कैम चैनल @RoyalForex_VIP से मेल खाता है (विश्वसनीयता स्कोर 0.98)।'
          : 'CRITICAL: Matched blacklisted scam channel @RoyalForex_VIP (Confidence Score 0.98).',
        language === 'hi'
          ? 'अवास्तविक लाभ का वादा: 35% दैनिक रिटर्न वित्तीय रूप से असंभव है।'
          : 'Unfeasible Return Promise: 35% daily return is mathematically impossible.',
        language === 'hi'
          ? 'गैर-कानूनी दबाव: सीमित सीटें और गारंटीड रिटर्न का फर्जी दावा।'
          : 'FOMO Trigger: False claim of 100% profit guarantee and limited seats.',
      ],
      analysisVernacular:
        language === 'hi'
          ? '⚠️ **अत्यधिक गंभीर धोखाधड़ी चेतावनी (जोखिम: 98%)**\nयह संदेश एक प्रमाणित पोंजी स्कैम है। SEBI कभी भी लाभ की गारंटी नहीं देता। कृपया कोई पैसा न भेजें।'
          : '⚠️ **CRITICAL FRAUD WARNING (Risk: 98%)**\nThis offer is a verified Ponzi scam. SEBI never guarantees profits. Do not send any money.',
      matchedRegInfo: null,
      extractedText: inputText,
      extractedUpi: 'scammer10x@ybl',
      extractedRegNumber: undefined,
      deceptionMetrics: {
        yieldRisk: 98,
        fomoRisk: 95,
        registryMatch: 0,
      },
    };
  }

  // Seed Case 2: SEBI Registered RIA Check
  if (
    textLower.includes('ina000012345') ||
    textLower.includes('apex capital') ||
    textLower.includes('registered ria')
  ) {
    return {
      verdict: 'SAFE',
      riskScore: 0.05,
      flags: [
        language === 'hi'
          ? 'सत्यापित SEBI पंजीकरण नंबर INA000012345 (Apex Capital Wealth Advisors).'
          : 'Verified Active SEBI Registration INA000012345 (Apex Capital Wealth Advisors).',
        language === 'hi'
          ? 'कोई अनैतिक गारंटीड रिटर्न दावा नहीं मिला।'
          : 'No unauthorized guaranteed return claims detected.',
      ],
      analysisVernacular:
        language === 'hi'
          ? '✅ **सत्यापित सुरक्षित सलाहकार (जोखिम: 5%)**\nयह संस्था SEBI के साथ पंजीकृत Investment Advisor (RIA) के रूप में सक्रिय है।'
          : '✅ **VERIFIED REGISTERED ADVISOR (Risk: 5%)**\nThis entity is actively registered with SEBI as a Investment Adviser (RIA).',
      matchedRegInfo: {
        reg_number: 'INA000012345',
        entity_name: 'Apex Capital Wealth Advisors',
        category: 'RIA',
        status: 'ACTIVE',
        valid_until: '2028-12-31',
        complaint_count: 1,
      },
      extractedText: inputText,
      extractedUpi: 'apexcapital@icici',
      extractedRegNumber: 'INA000012345',
      deceptionMetrics: {
        yieldRisk: 5,
        fomoRisk: 10,
        registryMatch: 100,
      },
    };
  }

  // Seed Case 3: Dabba Trading Clone App / Suspicious
  if (
    textLower.includes('dabba') ||
    textLower.includes('niftydabbaking') ||
    textLower.includes('no demat') ||
    textLower.includes('off-exchange')
  ) {
    return {
      verdict: 'SUSPICIOUS',
      riskScore: 0.72,
      flags: [
        language === 'hi'
          ? 'डब्बा ट्रेडिंग / अनधिकृत ऑफ-एक्सचेंज ट्रेडिंग के संकेत मिले।'
          : 'Dabba Trading / Unrecognized Off-Exchange trading signals detected.',
        language === 'hi'
          ? 'बिना डिमैट खाते के ट्रेड का फर्जी आश्वासन।'
          : 'Suspicious claim of trading without recognized SEBI Demat account.',
      ],
      analysisVernacular:
        language === 'hi'
          ? '⚡ **संदिग्ध गैर-कानूनी प्लेटफॉर्म (जोखिम: 72%)**\nयह ऐप अनधिकृत डब्बा ट्रेडिंग का संकेत देता है। स्टॉक एक्सचेंज सुरक्षा उपलब्ध नहीं है।'
          : '⚡ **SUSPICIOUS UNRECOGNIZED PLATFORM (Risk: 72%)**\nThis app shows hallmarks of illegal Dabba trading without exchange protection.',
      matchedRegInfo: null,
      extractedText: inputText,
      extractedUpi: 'dabbaking@paytm',
      extractedRegNumber: undefined,
      deceptionMetrics: {
        yieldRisk: 75,
        fomoRisk: 80,
        registryMatch: 0,
      },
    };
  }

  // Default fallback heuristic calculation
  return {
    verdict: 'SUSPICIOUS',
    riskScore: 0.45,
    flags: [
      language === 'hi'
        ? 'संदेश में कुछ गैर-मानक वित्तीय दावे हैं। ध्यानपूर्वक जांच करें।'
        : 'Message contains non-standard financial promises. Verify carefully.',
    ],
    analysisVernacular:
      language === 'hi'
        ? '⚡ **सतर्कता आवश्यक (जोखिम: 45%)**\nप्रस्ताव में आंशिक जोखिम के लक्षण हैं। केवल SEBI पंजीकृत संस्थाओं को ही शुल्क दें।'
        : '⚡ **CAUTION ADVISED (Risk: 45%)**\nModerate risk markers present. Verify regulatory credentials before transferring funds.',
    matchedRegInfo: null,
    extractedText: inputText,
    extractedUpi: undefined,
    extractedRegNumber: undefined,
    deceptionMetrics: {
      yieldRisk: 40,
      fomoRisk: 50,
      registryMatch: 20,
    },
  };
}

export async function generateSyntheticDossier(
  incidentSummary: string,
  amount: number,
  scammerDetails: Record<string, any>
): Promise<GrievanceDossier> {
  await new Promise((resolve) => setTimeout(resolve, 800));

  const regNumber = scammerDetails.reg_number;
  const isSebi = Boolean(regNumber);
  const filingPortal = isSebi ? 'SEBI_SCORES' : 'CYBERCRIME_PORTAL';

  const markdown = `# FORMAL COMPLAINT DOSSIER
**Generated by Sangyan Rakshak Scam Shield Engine**  
**Date:** ${new Date().toISOString().split('T')[0]}  
**Filing Target Portal:** ${filingPortal}  

---

### I. INCIDENT SUMMARY & PARTICULARS
* **Target Entity / Scammer:** ${scammerDetails.intermediary_name || scammerDetails.channel_handle || 'Unregistered Handle'}
* **SEBI Registration Number:** \`${regNumber || 'UNREGISTERED / NONE'}\`
* **UPI / Account Identifier:** \`${scammerDetails.upi_id || 'N/A'}\`
* **Total Disputed Financial Losses:** ₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })} INR

---

### II. NARRATIVE EVIDENCE
> ${incidentSummary}

---

### III. LEGAL PRAYER & RELIEF
1. Immediate freezing of account associated with \`${scammerDetails.upi_id || 'disputed transaction'}\`.
2. Directive for full restitution of ₹${amount.toLocaleString('en-IN')} INR under SEBI / IT Act provisions.
3. Permanent blocking orders against channel \`${scammerDetails.channel_handle || 'N/A'}\`.

---
*Formatted for official upload to ${filingPortal} under Section 65B of Indian Evidence Act.*
`;

  return {
    dossierMarkdown: markdown,
    filingPortal,
    requiredDocuments: [
      'Bank transaction statement highlighting UPI transfer',
      'Telegram/WhatsApp chat transcript screenshots',
      'UPI Transaction UTR / RRN Reference Receipts',
      'Identity Proof (Aadhaar / PAN Card)',
      'Sangyan Rakshak SEBI Audit Log Certificate',
    ],
  };
}
