import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useLanguage } from '../hooks/useLanguage';
import { useCropRecommendations, useWeatherData, useFarmingTips, useAIConversations, useSoilAnalysis } from '../hooks/useAgriculturalData';
import { Mic, MicOff, Volume2, Lightbulb, Sprout, TestTube, Settings } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { processMockQuery, MockApiResponse } from '../lib/mockApiSystem';
import StatusIndicator from './StatusIndicator';

interface SmartAIAssistantProps {
  currentLanguage: string;
}

export const SmartAIAssistant: React.FC<SmartAIAssistantProps> = ({ currentLanguage }) => {
  const { translations } = useLanguage();
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [recognition, setRecognition] = useState<any>(null);
  const [currentLocation, setCurrentLocation] = useState('Karnataka');
  const [useMockApi, setUseMockApi] = useState(true);
  const [mockResponse, setMockResponse] = useState<MockApiResponse | null>(null);

  const { data: cropRecommendations } = useCropRecommendations(currentLocation, 'kharif');
  const { data: weatherData } = useWeatherData('Bangalore');
  const { data: farmingTips } = useFarmingTips();
  const { saveConversation } = useAIConversations();
  const { getSoilAnalysisHistory } = useSoilAnalysis();

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = currentLanguage === 'kannada' ? 'kn-IN' : 'en-IN';

      recognitionInstance.onresult = (event: any) => {
        const lastResult = event.results[event.results.length - 1];
        const transcript = lastResult[0].transcript;
        setTranscript(transcript);
        
        if (lastResult.isFinal) {
          processVoiceQuery(transcript);
          setIsListening(false);
        }
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        toast.error('Voice recognition failed. Please try again.');
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, [currentLanguage]);

  const processVoiceQuery = async (query: string) => {
    console.log('Processing voice query:', query);
    
    // Use Mock API System if enabled
    if (useMockApi) {
      const mockApiResponse = processMockQuery(query, currentLanguage);
      setMockResponse(mockApiResponse);
      
      const finalResponse = currentLanguage === 'kn' ? mockApiResponse.responseKannada : 
                           currentLanguage === 'hi' ? mockApiResponse.responseHindi : 
                           mockApiResponse.response;
      setAiResponse(finalResponse);
      
      // Text-to-speech for mock response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(finalResponse);
        utterance.lang = currentLanguage === 'kannada' ? 'kn-IN' : 'en-IN';
        speechSynthesis.speak(utterance);
      }
      
      return;
    }
    
    // Enhanced AI logic with soil analysis integration (fallback)
    let response = '';
    let responseKannada = '';

    const queryLower = query.toLowerCase();
    
    if (queryLower.includes('soil') || queryLower.includes('ಮಣ್ಣು') || queryLower.includes('test') || queryLower.includes('ಪರೀಕ್ಷೆ')) {
      response = `KisaanMitra's Geo-Agronomy Agent (GAA) can analyze your soil and recommend optimal crop portfolios for collective farming! Provide your soil's NPK values, pH, temperature, humidity, and rainfall data for AI-powered recommendations.`;
      responseKannada = `ಕಿಸಾನ್‌ಮಿತ್ರದ ಜಿಯೋ-ಅಗ್ರೋನಮಿ ಏಜೆಂಟ್ (GAA) ನಿಮ್ಮ ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಸಾಮೂಹಿಕ ಕೃಷಿಗಾಗಿ ಅತ್ಯುತ್ತಮ ಬೆಳೆ ಪೋರ್ಟ್‌ಫೋಲಿಯೊಗಳನ್ನು ಶಿಫಾರಸು ಮಾಡಬಹುದು!`;
    } else if (queryLower.includes('crop') || queryLower.includes('ಬೆಳೆ') || queryLower.includes('plant') || queryLower.includes('portfolio')) {
      const bestCrop = cropRecommendations?.[0];
      if (bestCrop) {
        response = `Based on market intelligence, I recommend ${bestCrop.crop_name} for your FPO collective. Profitability score: ${bestCrop.profitability_score}%, growing duration: ${bestCrop.growing_duration} days. Our CMGA agent optimizes crop portfolios for maximum collective profit!`;
        responseKannada = `ಮಾರುಕಟ್ಟೆ ಬುದ್ಧಿವಂತಿಕೆಯ ಆಧಾರದ ಮೇಲೆ, ನಿಮ್ಮ FPO ಸಾಮೂಹಿಕಕ್ಕಾಗಿ ${bestCrop.crop_name === 'Rice' ? 'ಅಕ್ಕಿ' : bestCrop.crop_name === 'Wheat' ? 'ಗೋಧಿ' : bestCrop.crop_name} ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ!`;
      }
    } else if (queryLower.includes('weather') || queryLower.includes('ಹವಾಮಾನ') || queryLower.includes('rain') || queryLower.includes('climate')) {
      const todayWeather = weatherData?.[0];
      if (todayWeather) {
        response = `Climate & Resource Agent (CRA) reports: ${todayWeather.temperature}°C, ${todayWeather.humidity}% humidity, ${todayWeather.rainfall}mm rainfall. Condition: ${todayWeather.weather_condition}. Our IoT sensors monitor field conditions 24/7 for optimal irrigation!`;
        responseKannada = `CRA ಏಜೆಂಟ್ ವರದಿ: ${todayWeather.temperature}°C, ${todayWeather.humidity}% ಆರ್ದ್ರತೆ, ${todayWeather.rainfall}mm ಮಳೆ.`;
      }
    } else if (queryLower.includes('tip') || queryLower.includes('advice') || queryLower.includes('ಸಲಹೆ')) {
      const randomTip = farmingTips?.[Math.floor(Math.random() * (farmingTips?.length || 1))];
      if (randomTip) {
        response = `Expert farming tip from KisaanMitra: ${randomTip.tip_title}. ${randomTip.tip_content}`;
        responseKannada = `ಕಿಸಾನ್‌ಮಿತ್ರದಿಂದ ತಜ್ಞರ ಸಲಹೆ: ${randomTip.tip_title_kannada}. ${randomTip.tip_content_kannada}`;
      }
    } else if (queryLower.includes('fpo') || queryLower.includes('collective') || queryLower.includes('market')) {
      response = "KisaanMitra helps you join Farmer Producer Organizations (FPOs) for collective market governance! Our Market Intelligence Agent (MIA) provides real-time mandi prices and demand forecasting. Join an FPO to increase bargaining power and profits!";
      responseKannada = "ಕಿಸಾನ್‌ಮಿತ್ರ FPO ಗಳಿಗೆ ಸೇರಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ! ನಮ್ಮ MIA ಏಜೆಂಟ್ ನೇರ ಮಂಡಿ ಬೆಲೆಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ!";
    } else {
      response = "KisaanMitra's 7 AI agents are here to help! Ask about: crop portfolios (CMGA), market prices (MIA), soil analysis (GAA), weather (CRA), loans (FIA), cold storage (LIA), or FPO collectives. Transforming farmers into shareholders!";
      responseKannada = "ಕಿಸಾನ್‌ಮಿತ್ರದ 7 AI ಏಜೆಂಟ್‌ಗಳು ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿವೆ! ಬೆಳೆ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಮಣ್ಣು, ಹವಾಮಾನ, ಸಾಲ, FPO ಬಗ್ಗೆ ಕೇಳಿ!";
    }

    const finalResponse = currentLanguage === 'kannada' ? responseKannada : response;
    setAiResponse(finalResponse);

    // Save conversation to database
    try {
      await saveConversation.mutateAsync({
        user_query: query,
        user_query_kannada: currentLanguage === 'kannada' ? query : undefined,
        ai_response: response,
        ai_response_kannada: responseKannada,
        language: currentLanguage,
        location: currentLocation
      });
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }

    // Text-to-speech for AI response
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(finalResponse);
      utterance.lang = currentLanguage === 'kannada' ? 'kn-IN' : 'en-IN';
      speechSynthesis.speak(utterance);
    }
  };

  const startListening = () => {
    if (recognition) {
      setTranscript('');
      setAiResponse('');
      setIsListening(true);
      recognition.start();
    } else {
      // Fallback for demo
      const mockQueries = {
        kannada: 'ಈ ವಾರ ಯಾವ ಬೆಳೆ ಬೆಳೆಸೋದು ಲಾಭಕಾರಿಯಿರುತ್ತೆ?',
        english: 'Which crop should I plant this week?'
      };
      const mockQuery = mockQueries[currentLanguage as keyof typeof mockQueries] || mockQueries.english;
      processVoiceQuery(mockQuery);
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
    }
    setIsListening(false);
  };

  const speakResponse = () => {
    if ('speechSynthesis' in window && aiResponse) {
      const utterance = new SpeechSynthesisUtterance(aiResponse);
      utterance.lang = currentLanguage === 'kannada' ? 'kn-IN' : 'en-IN';
      speechSynthesis.speak(utterance);
    }
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-green-50 to-blue-50 border-green-200">
      <div className="text-center space-y-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sprout className="text-green-600" size={32} />
            <h2 className="text-2xl font-bold text-green-800">
              {currentLanguage === 'kannada' ? 'ಕಿಸಾನ್‌ಮಿತ್ರ AI ಸಹಾಯಕ' : currentLanguage === 'hindi' ? 'किसानमित्र AI सहायक' : 'KisaanMitra AI Assistant'}
            </h2>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
              {currentLanguage === 'kannada' ? '7 ಏಜೆಂಟ್‌ಗಳು' : currentLanguage === 'hindi' ? '7 एजेंट' : '7 Agents'}
            </span>
          </div>
          
          <Button
            onClick={() => setUseMockApi(!useMockApi)}
            variant="outline"
            size="sm"
            className={`${useMockApi ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-gray-50'}`}
          >
            <Settings className="w-4 h-4 mr-1" />
            {useMockApi ? 'Mock API' : 'Live API'}
          </Button>
        </div>
        
        {/* Voice Button */}
        <div className="relative">
          <Button
            onClick={isListening ? stopListening : startListening}
            size="lg"
            className={`
              w-24 h-24 rounded-full text-white font-semibold text-lg shadow-lg transition-all duration-300 transform
              ${isListening 
                ? 'bg-red-500 hover:bg-red-600 scale-110 animate-pulse' 
                : 'bg-green-500 hover:bg-green-600 hover:scale-105'
              }
            `}
          >
            {isListening ? <MicOff size={32} /> : <Mic size={32} />}
          </Button>
          
          {isListening && (
            <div className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping"></div>
          )}
        </div>

        <p className="text-green-700 font-medium">
          {isListening 
            ? (currentLanguage === 'kannada' ? 'ಕೇಳುತ್ತಿದೆ... ಮಾತನಾಡಿ' : 'Listening... Speak now')
            : (currentLanguage === 'kannada' ? 'ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಮಾತನಾಡಿ' : 'Tap microphone to speak')
          }
        </p>

        {/* Transcript Display */}
        {transcript && (
          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-blue-600 font-semibold">
                {currentLanguage === 'kannada' ? 'ನೀವು ಹೇಳಿದ್ದು:' : 'You said:'}
              </span>
            </div>
            <p className="text-blue-800">{transcript}</p>
          </Card>
        )}

        {/* AI Response */}
        {mockResponse && useMockApi ? (
          <StatusIndicator response={mockResponse} language={currentLanguage} />
        ) : aiResponse && (
          <Card className="p-4 bg-green-50 border-green-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-green-600 font-semibold flex items-center space-x-2">
                <Lightbulb size={20} />
                <span>{currentLanguage === 'kannada' ? 'AI ಉತ್ತರ:' : 'AI Response:'}</span>
              </span>
              <Button
                onClick={speakResponse}
                size="sm"
                variant="outline"
                className="text-green-600 border-green-300"
              >
                <Volume2 size={16} />
              </Button>
            </div>
            <p className="text-green-800">{aiResponse}</p>
          </Card>
        )}

        {/* Quick Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Button 
            onClick={() => processVoiceQuery(currentLanguage === 'kannada' ? 'ಯಾವ ಬೆಳೆ ಬೆಳೆಸೋದು?' : 'What crop to grow?')}
            variant="outline" 
            className="text-green-600 border-green-300 hover:bg-green-50"
          >
            🌱 {currentLanguage === 'kannada' ? 'ಬೆಳೆ ಸಲಹೆ' : 'Crop Advice'}
          </Button>
          <Button 
            onClick={() => processVoiceQuery(currentLanguage === 'kannada' ? 'ಹವಾಮಾನ ಹೇಗಿದೆ?' : 'How is the weather?')}
            variant="outline" 
            className="text-blue-600 border-blue-300 hover:bg-blue-50"
          >
            🌤️ {currentLanguage === 'kannada' ? 'ಹವಾಮಾನ' : 'Weather'}
          </Button>
          <Button 
            onClick={() => navigate('/soil-analysis')}
            variant="outline" 
            className="text-amber-600 border-amber-300 hover:bg-amber-50"
          >
            <TestTube size={16} className="mr-1" />
            {currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ' : 'Soil Test'}
          </Button>
          <Button 
            onClick={() => processVoiceQuery(currentLanguage === 'kannada' ? 'ಮಳೆ ಬರುತ್ತೆಯಾ?' : 'Will it rain?')}
            variant="outline" 
            className="text-purple-600 border-purple-300 hover:bg-purple-50"
          >
            🌧️ {currentLanguage === 'kannada' ? 'ಮಳೆ ಮುನ್ಸೂಚನೆ' : 'Rain Forecast'}
          </Button>
        </div>
      </div>
    </Card>
  );
};
