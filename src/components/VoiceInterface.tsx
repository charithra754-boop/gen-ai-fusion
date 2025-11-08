
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useLanguage } from '../hooks/useLanguage';

interface VoiceInterfaceProps {
  onVoiceQuery: (query: string) => void;
  isListening: boolean;
  setIsListening: (listening: boolean) => void;
  currentLanguage: string;
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onVoiceQuery,
  isListening,
  setIsListening,
  currentLanguage
}) => {
  const { translations } = useLanguage();
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = currentLanguage === 'kannada' ? 'kn-IN' : 'en-IN';

      recognitionInstance.onstart = () => {
        console.log('Speech recognition started');
      };

      recognitionInstance.onresult = (event: any) => {
        const lastResult = event.results[event.results.length - 1];
        const transcript = lastResult[0].transcript;
        setTranscript(transcript);
        
        if (lastResult.isFinal) {
          onVoiceQuery(transcript);
          setIsListening(false);
        }
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, [currentLanguage, onVoiceQuery, setIsListening]);

  const startListening = () => {
    if (recognition) {
      setTranscript('');
      setIsListening(true);
      recognition.start();
    } else {
      // Fallback for browsers without speech recognition
      const mockQuery = currentLanguage === 'kannada' 
        ? 'ಈ ವಾರ ಯಾವ ಬೆಳೆ ಬೆಳೆಸೋದು ಲಾಭಕಾರಿಯಿರುತ್ತೆ?'
        : 'Which crop should I plant this week?';
      onVoiceQuery(mockQuery);
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
    }
    setIsListening(false);
  };

  return (
    <div className="bg-white rounded-2xl p-8 shadow-xl border border-green-100">
      <div className="text-center space-y-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          {translations.askAgroMind}
        </h2>
        
        {/* Voice Button */}
        <div className="relative">
          <Button
            onClick={isListening ? stopListening : startListening}
            className={`
              w-24 h-24 rounded-full text-white font-semibold text-lg shadow-lg transition-all duration-300 transform
              ${isListening 
                ? 'bg-red-500 hover:bg-red-600 scale-110 animate-pulse' 
                : 'bg-green-500 hover:bg-green-600 hover:scale-105'
              }
            `}
          >
            {isListening ? '🛑' : '🎤'}
          </Button>
          
          {isListening && (
            <div className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping"></div>
          )}
        </div>

        <p className="text-gray-600">
          {isListening ? translations.listening : translations.tapToSpeak}
        </p>

        {/* Transcript Display */}
        {transcript && (
          <div className="bg-green-50 rounded-lg p-4 mt-4">
            <p className="text-green-800 font-medium">{transcript}</p>
          </div>
        )}

        {/* Sample Queries */}
        <div className="text-left space-y-2">
          <h3 className="font-semibold text-gray-700 text-center mb-3">
            {translations.sampleQuestions}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-600">
                {currentLanguage === 'kannada' 
                  ? 'ಈ ಕಾಲದಲ್ಲಿ ಯಾವ ಬೆಳೆ ಬೆಳೆಸೋದು?'
                  : 'Which crop to grow this season?'
                }
              </span>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-600">
                {currentLanguage === 'kannada'
                  ? 'ಮಳೆ ಬರೋ ಸಾಧ್ಯತೆ ಇದ್ಯಾ?'
                  : 'Will it rain this week?'
                }
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
