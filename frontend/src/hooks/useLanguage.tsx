
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface LanguageContextType {
  currentLanguage: string;
  setLanguage: (language: string) => void;
  translations: Record<string, string>;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations = {
  english: {
    askAgroMind: "Ask KisaanMitra",
    listening: "Listening... Speak now",
    tapToSpeak: "Tap microphone to speak",
    sampleQuestions: "Sample Questions:",
    cropAdvice: "Collective Farming",
    cropAdviceDesc: "Join FPOs for collective market governance and better profits",
    waterManagement: "Smart Resources",
    waterManagementDesc: "IoT-enabled irrigation and climate-resilient farming",
    weather: "Market Intelligence",
    weatherDesc: "Real-time mandi prices and demand forecasting",
    cropRecommendations: "Crop Portfolio",
    cropRecommendationsDesc: "AI-optimized crop planning for your collective",
    irrigation: "Smart Irrigation",
    irrigationDesc: "Autonomous water management",
    weatherForecast: "Climate & Weather",
    weatherForecastDesc: "Satellite imagery and weather predictions",
    recommendedCrop: "Recommended Crop",
    recommendedFor: "Recommended for",
    confidence: "Confidence Level",
    todaysWeather: "Today's Weather",
    temperature: "Temperature",
    humidity: "Humidity",
    rainfall: "Rainfall",
    goodForFarming: "Good conditions for farming",
    farmingTips: "Expert Farming Tips",
    aiAssistant: "Multi-Agent AI Assistant",
    soilAnalysis: "Soil Analysis",
    testYourSoil: "Test Your Soil",
    enterSoilParameters: "Enter your soil parameters to get AI-powered crop recommendations for collective farming",
    nitrogen: "Nitrogen (N)",
    phosphorus: "Phosphorus (P)",
    potassium: "Potassium (K)",
    ph: "pH Level",
    analyzeNow: "Analyze Now",
    analyzing: "Analyzing...",
    soilTestResults: "Soil Test Results",
    alternativeCrops: "Alternative Crops"
  },
  kannada: {
    askAgroMind: "ಕಿಸಾನ್‌ಮಿತ್ರ ಅನ್ನು ಕೇಳಿ",
    listening: "ಕೇಳುತ್ತಿದೆ... ಈಗ ಮಾತನಾಡಿ",
    tapToSpeak: "ಮಾತನಾಡಲು ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ",
    sampleQuestions: "ಮಾದರಿ ಪ್ರಶ್ನೆಗಳು:",
    cropAdvice: "ಸಾಮೂಹಿಕ ಕೃಷಿ",
    cropAdviceDesc: "ಉತ್ತಮ ಲಾಭಕ್ಕಾಗಿ FPO ಗಳಿಗೆ ಸೇರಿ",
    waterManagement: "ಸ್ಮಾರ್ಟ್ ಸಂಪನ್ಮೂಲಗಳು",
    waterManagementDesc: "IoT ನೀರಾವರಿ ಮತ್ತು ಹವಾಮಾನ-ಸ್ಥಿತಿಸ್ಥಾಪಕ ಕೃಷಿ",
    weather: "ಮಾರುಕಟ್ಟೆ ಬುದ್ಧಿವಂತಿಕೆ",
    weatherDesc: "ನೇರ ಮಂಡಿ ಬೆಲೆಗಳು ಮತ್ತು ಬೇಡಿಕೆ ಮುನ್ಸೂಚನೆ",
    cropRecommendations: "ಬೆಳೆ ಪೋರ್ಟ್‌ಫೋಲಿಯೋ",
    cropRecommendationsDesc: "ನಿಮ್ಮ ಸಾಮೂಹಿಕಕ್ಕಾಗಿ AI-ಆಧಾರಿತ ಬೆಳೆ ಯೋಜನೆ",
    irrigation: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ",
    irrigationDesc: "ಸ್ವಯಂಚಾಲಿತ ನೀರು ನಿರ್ವಹಣೆ",
    weatherForecast: "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",
    weatherForecastDesc: "ಉಪಗ್ರಹ ಚಿತ್ರಗಳು ಮತ್ತು ಹವಾಮಾನ ಭವಿಷ್ಯವಾಣಿಗಳು",
    recommendedCrop: "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ",
    recommendedFor: "ಇದಕ್ಕಾಗಿ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ",
    confidence: "ವಿಶ್ವಾಸ ಮಟ್ಟ",
    todaysWeather: "ಇಂದಿನ ಹವಾಮಾನ",
    temperature: "ತಾಪಮಾನ",
    humidity: "ಆರ್ದ್ರತೆ",
    rainfall: "ಮಳೆ",
    goodForFarming: "ಕೃಷಿಗೆ ಒಳ್ಳೆಯ ಪರಿಸ್ಥಿತಿಗಳು",
    farmingTips: "ತಜ್ಞರ ಕೃಷಿ ಸಲಹೆಗಳು",
    aiAssistant: "ಬಹು-ಏಜೆಂಟ್ AI ಸಹಾಯಕ",
    soilAnalysis: "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ",
    testYourSoil: "ನಿಮ್ಮ ಮಣ್ಣನ್ನು ಪರೀಕ್ಷಿಸಿ",
    enterSoilParameters: "ಸಾಮೂಹಿಕ ಕೃಷಿಗಾಗಿ AI-ಚಾಲಿತ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಲು ಮಣ್ಣಿನ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ",
    nitrogen: "ಸಾರಜನಕ (N)",
    phosphorus: "ರಂಜಕ (P)",
    potassium: "ಪೊಟ್ಯಾಸಿಯಮ್ (K)",
    ph: "pH ಮಟ್ಟ",
    analyzeNow: "ಈಗ ವಿಶ್ಲೇಷಿಸಿ",
    analyzing: "ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
    soilTestResults: "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಯ ಫಲಿತಾಂಶಗಳು",
    alternativeCrops: "ಪರ್ಯಾಯ ಬೆಳೆಗಳು"
  },
  hindi: {
    askAgroMind: "किसानमित्र से पूछें",
    listening: "सुन रहा है... अब बोलें",
    tapToSpeak: "बोलने के लिए माइक्रोफोन दबाएं",
    sampleQuestions: "नमूना प्रश्न:",
    cropAdvice: "सामूहिक खेती",
    cropAdviceDesc: "बेहतर मुनाफे के लिए FPO में शामिल हों",
    waterManagement: "स्मार्ट संसाधन",
    waterManagementDesc: "IoT सिंचाई और जलवायु-लचीली खेती",
    weather: "बाजार खुफिया",
    weatherDesc: "रीयल-टाइम मंडी कीमतें और मांग पूर्वानुमान",
    cropRecommendations: "फसल पोर्टफोलियो",
    cropRecommendationsDesc: "आपके सामूहिक के लिए AI-अनुकूलित फसल योजना",
    irrigation: "स्मार्ट सिंचाई",
    irrigationDesc: "स्वचालित जल प्रबंधन",
    weatherForecast: "मौसम पूर्वानुमान",
    weatherForecastDesc: "उपग्रह छवियां और मौसम भविष्यवाणी",
    recommendedCrop: "अनुशंसित फसल",
    recommendedFor: "के लिए अनुशंसित",
    confidence: "विश्वास स्तर",
    todaysWeather: "आज का मौसम",
    temperature: "तापमान",
    humidity: "आर्द्रता",
    rainfall: "वर्षा",
    goodForFarming: "खेती के लिए अच्छी स्थितियां",
    farmingTips: "विशेषज्ञ कृषि सुझाव",
    aiAssistant: "बहु-एजेंट AI सहायक",
    soilAnalysis: "मिट्टी विश्लेषण",
    testYourSoil: "अपनी मिट्टी का परीक्षण करें",
    enterSoilParameters: "सामूहिक खेती के लिए AI-संचालित फसल सिफारिशें प्राप्त करने हेतु मिट्टी पैरामीटर दर्ज करें",
    nitrogen: "नाइट्रोजन (N)",
    phosphorus: "फॉस्फोरस (P)",
    potassium: "पोटेशियम (K)",
    ph: "pH स्तर",
    analyzeNow: "अब विश्लेषण करें",
    analyzing: "विश्लेषण हो रहा है...",
    soilTestResults: "मिट्टी परीक्षण परिणाम",
    alternativeCrops: "वैकल्पिक फसलें"
  }
};

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [currentLanguage, setCurrentLanguage] = useState('english');

  const setLanguage = (language: string) => {
    setCurrentLanguage(language);
    localStorage.setItem('kisaanMitraLanguage', language);
  };

  const value = {
    currentLanguage,
    setLanguage,
    translations: translations[currentLanguage as keyof typeof translations] || translations.english
  };

  return (
    <LanguageContext.Provider value={value}>
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
