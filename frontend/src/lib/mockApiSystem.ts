/**
 * Static Mock API System for KisaanMitra
 * Provides agricultural query categorization and color-coded responses
 */

export interface MockApiResponse {
  id: string;
  category: 'PIN' | 'KCC' | 'STRESS' | 'SELL' | 'GENERAL';
  status: 'success' | 'warning' | 'error';
  statusColor: 'green' | 'orange' | 'red';
  confidence: number;
  response: string;
  responseKannada: string;
  responseHindi: string;
  icon: string;
  timestamp: string;
  metadata?: {
    agentType?: string;
    actionRequired?: boolean;
    urgency?: 'low' | 'medium' | 'high';
  };
}

export interface QueryCategory {
  keywords: string[];
  kannadaKeywords: string[];
  hindiKeywords: string[];
  category: MockApiResponse['category'];
  defaultStatus: MockApiResponse['status'];
  defaultColor: MockApiResponse['statusColor'];
}

// Agricultural query categories with multilingual support
const QUERY_CATEGORIES: QueryCategory[] = [
  {
    keywords: ['pin', 'fraud', 'scam', 'otp', 'cvv', 'password', 'bank', 'account', 'money transfer', 'upi'],
    kannadaKeywords: ['ಪಿನ್', 'ವಂಚನೆ', 'ಓಟಿಪಿ', 'ಬ್ಯಾಂಕ್', 'ಖಾತೆ', 'ಹಣ', 'ಯುಪಿಐ'],
    hindiKeywords: ['पिन', 'धोखाधड़ी', 'ओटीपी', 'बैंक', 'खाता', 'पैसा', 'यूपीआई'],
    category: 'PIN',
    defaultStatus: 'error',
    defaultColor: 'red'
  },
  {
    keywords: ['kcc', 'loan', 'credit', 'kisan credit card', 'interest', 'subsidy', 'pm-kisan', 'scheme'],
    kannadaKeywords: ['ಕೆಸಿಸಿ', 'ಸಾಲ', 'ಕ್ರೆಡಿಟ್', 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್', 'ಬಡ್ಡಿ', 'ಸಬ್ಸಿಡಿ', 'ಯೋಜನೆ'],
    hindiKeywords: ['केसीसी', 'लोन', 'क्रेडिट', 'किसान क्रेडिट कार्ड', 'ब्याज', 'सब्सिडी', 'योजना'],
    category: 'KCC',
    defaultStatus: 'success',
    defaultColor: 'green'
  },
  {
    keywords: ['stress', 'disease', 'pest', 'crop failure', 'drought', 'flood', 'emergency', 'help', 'problem'],
    kannadaKeywords: ['ಒತ್ತಡ', 'ರೋಗ', 'ಕೀಟ', 'ಬೆಳೆ ವಿಫಲತೆ', 'ಬರ', 'ಪ್ರವಾಹ', 'ತುರ್ತು', 'ಸಹಾಯ', 'ಸಮಸ್ಯೆ'],
    hindiKeywords: ['तनाव', 'बीमारी', 'कीट', 'फसल की विफलता', 'सूखा', 'बाढ़', 'आपातकाल', 'मदद', 'समस्या'],
    category: 'STRESS',
    defaultStatus: 'warning',
    defaultColor: 'orange'
  },
  {
    keywords: ['sell', 'market', 'price', 'mandi', 'buyer', 'harvest', 'profit', 'fpo', 'collective'],
    kannadaKeywords: ['ಮಾರಾಟ', 'ಮಾರುಕಟ್ಟೆ', 'ಬೆಲೆ', 'ಮಂಡಿ', 'ಖರೀದಿದಾರ', 'ಸುಗ್ಗಿ', 'ಲಾಭ', 'ಎಫ್‌ಪಿಒ'],
    hindiKeywords: ['बेचना', 'बाजार', 'कीमत', 'मंडी', 'खरीदार', 'फसल', 'लाभ', 'एफपीओ'],
    category: 'SELL',
    defaultStatus: 'success',
    defaultColor: 'green'
  }
];

// Mock response templates for each category
const RESPONSE_TEMPLATES = {
  PIN: {
    success: {
      en: "🔒 SECURITY ALERT: Never share your PIN, OTP, or CVV with anyone. KisaanMitra's Financial Inclusion Agent (FIA) detected potential fraud risk. Your account is secure.",
      kn: "🔒 ಭದ್ರತಾ ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ಪಿನ್, ಓಟಿಪಿ ಅಥವಾ ಸಿವಿವಿ ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ. FIA ವಂಚನೆ ಅಪಾಯವನ್ನು ಪತ್ತೆ ಮಾಡಿದೆ.",
      hi: "🔒 सुरक्षा चेतावनी: अपना पिन, ओटीपी या सीवीवी किसी के साथ साझा न करें। FIA ने धोखाधड़ी का जोखिम पाया है।"
    },
    warning: {
      en: "⚠️ FRAUD WARNING: Suspicious activity detected. Block the caller immediately. Contact your bank helpline. FIA is monitoring your account security.",
      kn: "⚠️ ವಂಚನೆ ಎಚ್ಚರಿಕೆ: ಅನುಮಾನಾಸ್ಪದ ಚಟುವಟಿಕೆ ಪತ್ತೆಯಾಗಿದೆ. ಕರೆ ಮಾಡುವವರನ್ನು ತಕ್ಷಣ ನಿರ್ಬಂಧಿಸಿ.",
      hi: "⚠️ धोखाधड़ी चेतावनी: संदिग्ध गतिविधि का पता चला। कॉलर को तुरंत ब्लॉक करें।"
    },
    error: {
      en: "🚨 CRITICAL FRAUD ALERT: Do NOT proceed with any transaction. This is a confirmed scam. Report to cyber crime helpline 1930 immediately.",
      kn: "🚨 ಗಂಭೀರ ವಂಚನೆ ಎಚ್ಚರಿಕೆ: ಯಾವುದೇ ವ್ಯವಹಾರವನ್ನು ಮುಂದುವರಿಸಬೇಡಿ. ಇದು ದೃಢೀಕೃತ ವಂಚನೆ.",
      hi: "🚨 गंभीर धोखाधड़ी अलर्ट: कोई भी लेनदेन न करें। यह पुष्ट घोटाला है।"
    }
  },
  KCC: {
    success: {
      en: "✅ KCC APPROVED: Kisan Credit Card offers 7% interest, reduced to 4% on timely repayment. Loan limit up to ₹3,00,000. FIA confirms your eligibility.",
      kn: "✅ ಕೆಸಿಸಿ ಅನುಮೋದಿತ: ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ 7% ಬಡ್ಡಿ, ಸಮಯಕ್ಕೆ ಮರುಪಾವತಿಯಲ್ಲಿ 4%. ಸಾಲದ ಮಿತಿ ₹3,00,000.",
      hi: "✅ केसीसी स्वीकृत: किसान क्रेडिट कार्ड 7% ब्याज, समय पर भुगतान पर 4%। ऋण सीमा ₹3,00,000 तक।"
    },
    warning: {
      en: "⚠️ KCC DOCUMENTATION: Additional documents required for loan approval. Visit nearest bank branch with land records and Aadhar card.",
      kn: "⚠️ ಕೆಸಿಸಿ ದಾಖಲೆಗಳು: ಸಾಲ ಅನುಮೋದನೆಗೆ ಹೆಚ್ಚುವರಿ ದಾಖಲೆಗಳು ಅಗತ್ಯ. ಭೂಮಿ ದಾಖಲೆಗಳೊಂದಿಗೆ ಬ್ಯಾಂಕ್‌ಗೆ ಭೇಟಿ ನೀಡಿ.",
      hi: "⚠️ केसीसी दस्तावेज़: ऋण अनुमोदन के लिए अतिरिक्त दस्तावेज़ आवश्यक। भूमि रिकॉर्ड के साथ बैंक जाएं।"
    },
    error: {
      en: "❌ KCC REJECTED: Application does not meet eligibility criteria. Contact FIA for alternative loan schemes and guidance.",
      kn: "❌ ಕೆಸಿಸಿ ತಿರಸ್ಕರಿಸಲಾಗಿದೆ: ಅರ್ಜಿ ಅರ್ಹತಾ ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸುವುದಿಲ್ಲ. ಪರ್ಯಾಯ ಯೋಜನೆಗಳಿಗಾಗಿ FIA ಸಂಪರ್ಕಿಸಿ.",
      hi: "❌ केसीसी अस्वीकृत: आवेदन पात्रता मानदंडों को पूरा नहीं करता। वैकल्पिक योजनाओं के लिए FIA से संपर्क करें।"
    }
  },
  STRESS: {
    success: {
      en: "🌱 CROP RECOVERY: GAA detected early intervention success. NDVI improving. Continue current treatment protocol. Yield forecast: positive.",
      kn: "🌱 ಬೆಳೆ ಚೇತರಿಕೆ: GAA ಆರಂಭಿಕ ಹಸ್ತಕ್ಷೇಪದ ಯಶಸ್ಸನ್ನು ಪತ್ತೆ ಮಾಡಿದೆ. NDVI ಸುಧಾರಿಸುತ್ತಿದೆ.",
      hi: "🌱 फसल रिकवरी: GAA ने प्रारंभिक हस्तक्षेप की सफलता का पता लगाया। NDVI में सुधार हो रहा है।"
    },
    warning: {
      en: "⚠️ CROP STRESS DETECTED: CRA monitoring shows declining NDVI. Immediate field inspection required. Possible pest/disease outbreak.",
      kn: "⚠️ ಬೆಳೆ ಒತ್ತಡ ಪತ್ತೆಯಾಗಿದೆ: CRA ಮೇಲ್ವಿಚಾರಣೆ NDVI ಕುಸಿತವನ್ನು ತೋರಿಸುತ್ತದೆ. ತಕ್ಷಣ ಕ್ಷೇತ್ರ ತಪಾಸಣೆ ಅಗತ್ಯ.",
      hi: "⚠️ फसल तनाव का पता चला: CRA निगरानी NDVI में गिरावट दिखाती है। तत्काल क्षेत्र निरीक्षण आवश्यक।"
    },
    error: {
      en: "🚨 CRITICAL CROP FAILURE: Severe NDVI decline detected. Emergency intervention needed. Contact agricultural extension officer immediately.",
      kn: "🚨 ಗಂಭೀರ ಬೆಳೆ ವಿಫಲತೆ: ತೀವ್ರ NDVI ಕುಸಿತ ಪತ್ತೆಯಾಗಿದೆ. ತುರ್ತು ಹಸ್ತಕ್ಷೇಪ ಅಗತ್ಯ.",
      hi: "🚨 गंभीर फसल विफलता: गंभीर NDVI गिरावट का पता चला। आपातकालीन हस्तक्षेप की आवश्यकता।"
    }
  },
  SELL: {
    success: {
      en: "💰 OPTIMAL SELLING TIME: MIA forecasts 15% price increase next week. Current mandi rate: ₹2,400/quintal. Hold for better profits.",
      kn: "💰 ಅತ್ಯುತ್ತಮ ಮಾರಾಟದ ಸಮಯ: MIA ಮುಂದಿನ ವಾರ 15% ಬೆಲೆ ಹೆಚ್ಚಳವನ್ನು ಮುನ್ಸೂಚಿಸುತ್ತದೆ. ಪ್ರಸ್ತುತ ಮಂಡಿ ದರ: ₹2,400/ಕ್ವಿಂಟಲ್.",
      hi: "💰 इष्टतम बिक्री समय: MIA अगले सप्ताह 15% मूल्य वृद्धि का पूर्वानुमान लगाता है। वर्तमान मंडी दर: ₹2,400/क्विंटल।"
    },
    warning: {
      en: "⚠️ MARKET VOLATILITY: Prices fluctuating. LIA suggests immediate transport to avoid storage costs. FPO collective selling recommended.",
      kn: "⚠️ ಮಾರುಕಟ್ಟೆ ಅಸ್ಥಿರತೆ: ಬೆಲೆಗಳು ಏರಿಳಿತವಾಗುತ್ತಿವೆ. ಶೇಖರಣಾ ವೆಚ್ಚವನ್ನು ತಪ್ಪಿಸಲು LIA ತಕ್ಷಣ ಸಾಗಣೆ ಸೂಚಿಸುತ್ತದೆ.",
      hi: "⚠️ बाजार अस्थिरता: कीमतें उतार-चढ़ाव में हैं। भंडारण लागत से बचने के लिए LIA तत्काल परिवहन का सुझाव देता है।"
    },
    error: {
      en: "❌ POOR MARKET CONDITIONS: Prices below production cost. CMGA advises holding crop or processing into value-added products.",
      kn: "❌ ಕಳಪೆ ಮಾರುಕಟ್ಟೆ ಪರಿಸ್ಥಿತಿಗಳು: ಉತ್ಪಾದನಾ ವೆಚ್ಚಕ್ಕಿಂತ ಕಡಿಮೆ ಬೆಲೆಗಳು. CMGA ಬೆಳೆಯನ್ನು ಹಿಡಿದಿಟ್ಟುಕೊಳ್ಳಲು ಸಲಹೆ ನೀಡುತ್ತದೆ.",
      hi: "❌ खराब बाजार स्थितियां: उत्पादन लागत से कम कीमतें। CMGA फसल रखने या मूल्य संवर्धित उत्पादों में प्रसंस्करण की सलाह देता है।"
    }
  },
  GENERAL: {
    success: {
      en: "🌾 KISAANMITRA READY: All 7 AI agents operational. Ask about crops (CMGA), weather (CRA), soil (GAA), loans (FIA), markets (MIA), logistics (LIA), or governance (HIA).",
      kn: "🌾 ಕಿಸಾನ್‌ಮಿತ್ರ ಸಿದ್ಧ: ಎಲ್ಲಾ 7 AI ಏಜೆಂಟ್‌ಗಳು ಕಾರ್ಯಾಚರಣೆಯಲ್ಲಿವೆ. ಬೆಳೆಗಳು, ಹವಾಮಾನ, ಮಣ್ಣು, ಸಾಲಗಳು, ಮಾರುಕಟ್ಟೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ.",
      hi: "🌾 किसानमित्र तैयार: सभी 7 AI एजेंट परिचालन में हैं। फसलों, मौसम, मिट्टी, ऋण, बाजारों के बारे में पूछें।"
    },
    warning: {
      en: "⚠️ SYSTEM STATUS: Some agents experiencing high load. Response time may be delayed. Core functionality available.",
      kn: "⚠️ ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ: ಕೆಲವು ಏಜೆಂಟ್‌ಗಳು ಹೆಚ್ಚಿನ ಲೋಡ್ ಅನುಭವಿಸುತ್ತಿದ್ದಾರೆ. ಪ್ರತಿಕ್ರಿಯೆ ಸಮಯ ವಿಳಂಬವಾಗಬಹುದು.",
      hi: "⚠️ सिस्टम स्थिति: कुछ एजेंट उच्च लोड का अनुभव कर रहे हैं। प्रतिक्रिया समय में देरी हो सकती है।"
    },
    error: {
      en: "❌ SYSTEM ERROR: Unable to process query. Please try again or contact support. Emergency agricultural helpline: 1551.",
      kn: "❌ ಸಿಸ್ಟಮ್ ದೋಷ: ಪ್ರಶ್ನೆಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗುವುದಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬೆಂಬಲವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
      hi: "❌ सिस्टम त्रुटि: क्वेरी को प्रोसेस करने में असमर्थ। कृपया पुनः प्रयास करें या सहायता से संपर्क करें।"
    }
  }
};

/**
 * Categorizes a user query and returns the appropriate category
 */
export function categorizeQuery(query: string, language: string = 'en'): MockApiResponse['category'] {
  const queryLower = query.toLowerCase();
  
  for (const category of QUERY_CATEGORIES) {
    const keywordsToCheck = language === 'kn' ? category.kannadaKeywords : 
                          language === 'hi' ? category.hindiKeywords : 
                          category.keywords;
    
    const allKeywords = [...category.keywords, ...category.kannadaKeywords, ...category.hindiKeywords];
    
    if (allKeywords.some(keyword => queryLower.includes(keyword.toLowerCase()))) {
      return category.category;
    }
  }
  
  return 'GENERAL';
}

/**
 * Determines the status and color based on query content and category
 */
export function determineStatus(query: string, category: MockApiResponse['category']): {
  status: MockApiResponse['status'];
  color: MockApiResponse['statusColor'];
  confidence: number;
} {
  const queryLower = query.toLowerCase();
  
  // High-risk fraud indicators
  if (category === 'PIN') {
    if (queryLower.includes('share') || queryLower.includes('give') || queryLower.includes('tell')) {
      return { status: 'error', color: 'red', confidence: 95 };
    }
    if (queryLower.includes('forgot') || queryLower.includes('reset')) {
      return { status: 'warning', color: 'orange', confidence: 80 };
    }
    return { status: 'success', color: 'green', confidence: 90 };
  }
  
  // Crop stress severity
  if (category === 'STRESS') {
    if (queryLower.includes('dying') || queryLower.includes('dead') || queryLower.includes('failed')) {
      return { status: 'error', color: 'red', confidence: 90 };
    }
    if (queryLower.includes('yellow') || queryLower.includes('spots') || queryLower.includes('pest')) {
      return { status: 'warning', color: 'orange', confidence: 85 };
    }
    return { status: 'success', color: 'green', confidence: 75 };
  }
  
  // Market conditions
  if (category === 'SELL') {
    if (queryLower.includes('urgent') || queryLower.includes('emergency') || queryLower.includes('loss')) {
      return { status: 'warning', color: 'orange', confidence: 80 };
    }
    return { status: 'success', color: 'green', confidence: 85 };
  }
  
  // KCC loan status
  if (category === 'KCC') {
    if (queryLower.includes('rejected') || queryLower.includes('denied')) {
      return { status: 'error', color: 'red', confidence: 90 };
    }
    if (queryLower.includes('pending') || queryLower.includes('documents')) {
      return { status: 'warning', color: 'orange', confidence: 75 };
    }
    return { status: 'success', color: 'green', confidence: 85 };
  }
  
  // Default for general queries
  return { status: 'success', color: 'green', confidence: 70 };
}

/**
 * Generates a mock API response for agricultural queries
 */
export function generateMockResponse(query: string, language: string = 'en'): MockApiResponse {
  const category = categorizeQuery(query, language);
  const { status, color, confidence } = determineStatus(query, category);
  
  const template = RESPONSE_TEMPLATES[category][status];
  const response = language === 'kn' ? template.kn : 
                  language === 'hi' ? template.hi : 
                  template.en;
  
  const agentTypes = {
    PIN: 'FIA (Financial Inclusion Agent)',
    KCC: 'FIA (Financial Inclusion Agent)', 
    STRESS: 'GAA (Geo-Agronomy Agent)',
    SELL: 'MIA (Market Intelligence Agent)',
    GENERAL: 'Master Agent Orchestrator'
  };
  
  const icons = {
    PIN: '🔒',
    KCC: '💳',
    STRESS: '🌱',
    SELL: '💰',
    GENERAL: '🌾'
  };
  
  return {
    id: `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    category,
    status,
    statusColor: color,
    confidence,
    response,
    responseKannada: RESPONSE_TEMPLATES[category][status].kn,
    responseHindi: RESPONSE_TEMPLATES[category][status].hi,
    icon: icons[category],
    timestamp: new Date().toISOString(),
    metadata: {
      agentType: agentTypes[category],
      actionRequired: status !== 'success',
      urgency: status === 'error' ? 'high' : status === 'warning' ? 'medium' : 'low'
    }
  };
}

/**
 * Error types for query processing
 */
export interface QueryError {
  type: 'network' | 'validation' | 'timeout' | 'system' | 'unknown';
  message: string;
  code?: string;
  retryable: boolean;
}

/**
 * Validates query input and returns validation errors if any
 */
export function validateQuery(query: string): QueryError | null {
  if (!query || typeof query !== 'string') {
    return {
      type: 'validation',
      message: 'Query cannot be empty',
      retryable: false
    };
  }

  const trimmedQuery = query.trim();
  
  if (trimmedQuery.length === 0) {
    return {
      type: 'validation',
      message: 'Query cannot be empty',
      retryable: false
    };
  }

  if (trimmedQuery.length > 500) {
    return {
      type: 'validation',
      message: 'Query is too long. Please limit to 500 characters.',
      retryable: false
    };
  }

  // Check for potentially harmful content
  const suspiciousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /eval\s*\(/i
  ];

  if (suspiciousPatterns.some(pattern => pattern.test(trimmedQuery))) {
    return {
      type: 'validation',
      message: 'Query contains invalid characters',
      retryable: false
    };
  }

  return null;
}

/**
 * Creates a fallback response for unrecognized or problematic queries
 */
export function createFallbackResponse(query: string, error?: QueryError, language: string = 'en'): MockApiResponse {
  const fallbackMessages = {
    en: {
      unrecognized: "I didn't quite understand your question. Could you please rephrase it? You can ask about crops, loans (KCC), market prices, or security concerns.",
      validation: "Please check your question and try again. Make sure it's related to agriculture, finance, or farming.",
      network: "Connection issue detected. Please check your internet connection and try again.",
      timeout: "Request timed out. Please try again with a shorter question.",
      system: "System temporarily unavailable. Please try again in a few moments.",
      general: "Unable to process your request right now. Please try again or contact support."
    },
    kn: {
      unrecognized: "ನಿಮ್ಮ ಪ್ರಶ್ನೆ ನನಗೆ ಸರಿಯಾಗಿ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಅದನ್ನು ಮತ್ತೆ ಹೇಳಿ? ನೀವು ಬೆಳೆಗಳು, ಸಾಲಗಳು (KCC), ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಅಥವಾ ಭದ್ರತೆಯ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
      validation: "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ. ಇದು ಕೃಷಿ, ಹಣಕಾಸು ಅಥವಾ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದೆ ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
      network: "ಸಂಪರ್ಕ ಸಮಸ್ಯೆ ಪತ್ತೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
      timeout: "ವಿನಂತಿ ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಚಿಕ್ಕ ಪ್ರಶ್ನೆಯೊಂದಿಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
      system: "ಸಿಸ್ಟಮ್ ತಾತ್ಕಾಲಿಕವಾಗಿ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
      general: "ಇದೀಗ ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗುವುದಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬೆಂಬಲವನ್ನು ಸಂಪರ್ಕಿಸಿ."
    },
    hi: {
      unrecognized: "मुझे आपका प्रश्न ठीक से समझ नहीं आया। कृपया इसे दोबारा कहें? आप फसलों, ऋण (KCC), बाजार की कीमतों या सुरक्षा के बारे में पूछ सकते हैं।",
      validation: "कृपया अपने प्रश्न की जांच करें और पुनः प्रयास करें। सुनिश्चित करें कि यह कृषि, वित्त या खेती से संबंधित है।",
      network: "कनेक्शन समस्या का पता चला। कृपया अपना इंटरनेट कनेक्शन जांचें और पुनः प्रयास करें।",
      timeout: "अनुरोध का समय समाप्त हो गया। कृपया छोटे प्रश्न के साथ पुनः प्रयास करें।",
      system: "सिस्टम अस्थायी रूप से अनुपलब्ध है। कृपया कुछ क्षणों में पुनः प्रयास करें।",
      general: "अभी आपके अनुरोध को संसाधित करने में असमर्थ। कृपया पुनः प्रयास करें या सहायता से संपर्क करें।"
    }
  };

  const messages = fallbackMessages[language as keyof typeof fallbackMessages] || fallbackMessages.en;
  let message = messages.general;
  
  if (error) {
    switch (error.type) {
      case 'validation':
        message = messages.validation;
        break;
      case 'network':
        message = messages.network;
        break;
      case 'timeout':
        message = messages.timeout;
        break;
      case 'system':
        message = messages.system;
        break;
      default:
        message = messages.general;
    }
  } else {
    message = messages.unrecognized;
  }

  return {
    id: `fallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    category: 'GENERAL',
    status: 'error',
    statusColor: 'red',
    confidence: 0,
    response: message,
    responseKannada: fallbackMessages.kn[error?.type || 'unrecognized'] || fallbackMessages.kn.general,
    responseHindi: fallbackMessages.hi[error?.type || 'unrecognized'] || fallbackMessages.hi.general,
    icon: '❌',
    timestamp: new Date().toISOString(),
    metadata: {
      agentType: 'Error Handler',
      actionRequired: true,
      urgency: 'medium',
      errorType: error?.type || 'unrecognized',
      retryable: error?.retryable ?? true
    }
  };
}

/**
 * Processes a query and returns a mock API response with comprehensive error handling
 */
export function processMockQuery(query: string, language: string = 'en'): MockApiResponse {
  try {
    // Validate input
    const validationError = validateQuery(query);
    if (validationError) {
      console.warn(`Query validation failed: ${validationError.message}`);
      return createFallbackResponse(query, validationError, language);
    }

    // Simulate potential system errors (5% chance)
    if (Math.random() < 0.05) {
      const systemError: QueryError = {
        type: 'system',
        message: 'Simulated system error',
        retryable: true
      };
      console.warn('Simulated system error occurred');
      return createFallbackResponse(query, systemError, language);
    }

    // Process the query normally
    const response = generateMockResponse(query, language);
    
    // Check if the query was properly categorized
    if (response.category === 'GENERAL' && response.confidence < 50) {
      console.log(`Low confidence response for query: "${query}"`);
      return createFallbackResponse(query, undefined, language);
    }
    
    console.log(`Mock API: Processed query "${query}" -> Category: ${response.category}, Status: ${response.statusColor}`);
    
    return response;
  } catch (error) {
    console.error('Unexpected error in processMockQuery:', error);
    const systemError: QueryError = {
      type: 'unknown',
      message: 'Unexpected system error',
      retryable: true
    };
    return createFallbackResponse(query, systemError, language);
  }
}