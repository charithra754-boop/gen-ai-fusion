
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface LanguageContextType {
  currentLanguage: string;
  setLanguage: (language: string) => void;
  translations: Record<string, string>;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations = {
  english: {
    askAgroMind: "Ask AgroMind",
    listening: "Listening... Speak now",
    tapToSpeak: "Tap microphone to speak",
    sampleQuestions: "Sample Questions:",
    cropAdvice: "Crop Advice",
    cropAdviceDesc: "Get AI-powered crop recommendations based on real data",
    waterManagement: "Water Management",
    waterManagementDesc: "Smart irrigation schedules and water optimization",
    weather: "Weather",
    weatherDesc: "Real-time weather updates and forecasts",
    cropRecommendations: "Crop Recommendations",
    cropRecommendationsDesc: "AI-powered crop suggestions from database",
    irrigation: "Smart Irrigation",
    irrigationDesc: "Water management solutions",
    weatherForecast: "Weather Forecast",
    weatherForecastDesc: "7-day weather predictions",
    recommendedCrop: "Recommended Crop",
    recommendedFor: "Recommended for",
    confidence: "Confidence Level",
    todaysWeather: "Today's Weather",
    temperature: "Temperature",
    humidity: "Humidity", 
    rainfall: "Rainfall",
    goodForFarming: "Good conditions for farming",
    farmingTips: "Farming Tips",
    aiAssistant: "AI Assistant",
    soilAnalysis: "Soil Analysis",
    testYourSoil: "Test Your Soil",
    enterSoilParameters: "Enter your soil parameters to get AI-powered crop recommendations",
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
    askAgroMind: "ಅಗ್ರೋಮೈಂಡ್ ಅನ್ನು ಕೇಳಿ",
    listening: "ಕೇಳುತ್ತಿದೆ... ಈಗ ಮಾತನಾಡಿ",
    tapToSpeak: "ಮಾತನಾಡಲು ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ",
    sampleQuestions: "ಮಾದರಿ ಪ್ರಶ್ನೆಗಳು:",
    cropAdvice: "ಬೆಳೆ ಸಲಹೆ",
    cropAdviceDesc: "ನಿಜವಾದ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ AI ಬೆಳೆ ಶಿಫಾರಸುಗಳು",
    waterManagement: "ನೀರು ನಿರ್ವಹಣೆ",
    waterManagementDesc: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ನೀರಿನ ಉತ್ತಮೀಕರಣ",
    weather: "ಹವಾಮಾನ",
    weatherDesc: "ತಕ್ಷಣ ಹವಾಮಾನ ನವೀಕರಣಗಳು ಮತ್ತು ಮುನ್ಸೂಚನೆಗಳು",
    cropRecommendations: "ಬೆಳೆ ಶಿಫಾರಸುಗಳು",
    cropRecommendationsDesc: "ಡೇಟಾಬೇಸ್‌ನಿಂದ AI-ಚಾಲಿತ ಬೆಳೆ ಸಲಹೆಗಳು",
    irrigation: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ",
    irrigationDesc: "ನೀರು ನಿರ್ವಹಣೆ ಪರಿಹಾರಗಳು",
    weatherForecast: "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",
    weatherForecastDesc: "7-ದಿನಗಳ ಹವಾಮಾನ ಭವಿಷ್ಯವಾಣಿಗಳು",
    recommendedCrop: "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ",
    recommendedFor: "ಇದಕ್ಕಾಗಿ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ",
    confidence: "ವಿಶ್ವಾಸ ಮಟ್ಟ",
    todaysWeather: "ಇಂದಿನ ಹವಾಮಾನ",
    temperature: "ತಾಪಮಾನ",
    humidity: "ಆರ್ದ್ರತೆ",
    rainfall: "ಮಳೆ",
    goodForFarming: "ಕೃಷಿಗೆ ಒಳ್ಳೆಯ ಪರಿಸ್ಥಿತಿಗಳು",
    farmingTips: "ಕೃಷಿ ಸಲಹೆಗಳು",
    aiAssistant: "AI ಸಹಾಯಕ",
    soilAnalysis: "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ",
    testYourSoil: "ನಿಮ್ಮ ಮಣ್ಣನ್ನು ಪರೀಕ್ಷಿಸಿ",
    enterSoilParameters: "AI-ಚಾಲಿತ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಲು ನಿಮ್ಮ ಮಣ್ಣಿನ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ",
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
    askAgroMind: "एग्रोमाइंड से पूछें",
    listening: "सुन रहा है... अब बोलें",
    tapToSpeak: "बोलने के लिए माइक्रोफोन दबाएं",
    sampleQuestions: "नमूना प्रश्न:",
    cropAdvice: "फसल सलाह",
    cropAdviceDesc: "वास्तविक डेटा के आधार पर AI-संचालित फसल सिफारिशें",
    waterManagement: "जल प्रबंधन",
    waterManagementDesc: "स्मार्ट सिंचाई कार्यक्रम और जल अनुकूलन",
    weather: "मौसम",
    weatherDesc: "वास्तविक समय मौसम अपडेट और पूर्वानुमान",
    cropRecommendations: "फसल सिफारिशें",
    cropRecommendationsDesc: "डेटाबेस से AI-संचालित फसल सुझाव",
    irrigation: "स्मार्ट सिंचाई",
    irrigationDesc: "जल प्रबंधन समाधान",
    weatherForecast: "मौसम पूर्वानुमान",
    weatherForecastDesc: "7-दिन मौसम भविष्यवाणी",
    recommendedCrop: "अनुशंसित फसल",
    recommendedFor: "के लिए अनुशंसित",
    confidence: "विश्वास स्तर",
    todaysWeather: "आज का मौसम",
    temperature: "तापमान",
    humidity: "आर्द्रता",
    rainfall: "वर्षा",
    goodForFarming: "खेती के लिए अच्छी स्थितियां",
    farmingTips: "कृषि सुझाव",
    aiAssistant: "AI सहायक",
    soilAnalysis: "मिट्टी विश्लेषण",
    testYourSoil: "अपनी मिट्टी का परीक्षण करें",
    enterSoilParameters: "AI-संचालित फसल सिफारिशें प्राप्त करने के लिए अपनी मिट्टी के पैरामीटर दर्ज करें",
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
    localStorage.setItem('agroMindLanguage', language);
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
