import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Send, Mic, MicOff, History, RefreshCw } from 'lucide-react';
import { processMockQuery, MockApiResponse } from '../lib/mockApiSystem';
import StatusIndicator from './StatusIndicator';

interface MockQueryProcessorProps {
  language?: string;
}

export const MockQueryProcessor: React.FC<MockQueryProcessorProps> = ({ language = 'en' }) => {
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState<MockApiResponse[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Sample queries for demonstration
  const sampleQueries = {
    en: [
      "Someone asked for my PIN number",
      "How to apply for KCC loan?", 
      "My crops are turning yellow",
      "When should I sell my wheat?",
      "What is the weather forecast?"
    ],
    kn: [
      "ಯಾರೋ ನನ್ನ ಪಿನ್ ಸಂಖ್ಯೆ ಕೇಳಿದರು",
      "ಕೆಸಿಸಿ ಸಾಲಕ್ಕೆ ಹೇಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸುವುದು?",
      "ನನ್ನ ಬೆಳೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ",
      "ನನ್ನ ಗೋಧಿಯನ್ನು ಯಾವಾಗ ಮಾರಬೇಕು?",
      "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಏನು?"
    ],
    hi: [
      "किसी ने मेरा पिन नंबर मांगा",
      "केसीसी लोन के लिए कैसे आवेदन करें?",
      "मेरी फसलें पीली हो रही हैं", 
      "मुझे अपना गेहूं कब बेचना चाहिए?",
      "मौसम का पूर्वानुमान क्या है?"
    ]
  };

  const processQuery = async (inputQuery: string) => {
    if (!inputQuery.trim()) return;
    
    setIsProcessing(true);
    
    try {
      // Simulate API processing delay with timeout
      const processingPromise = new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 10000)
      );
      
      await Promise.race([processingPromise, timeoutPromise]);
      
      const response = processMockQuery(inputQuery, language);
      
      // Add retry functionality for failed requests
      if (response.status === 'error' && response.metadata?.retryable) {
        response.metadata.retryAction = () => processQuery(inputQuery);
      }
      
      setResponses(prev => [response, ...prev]);
      setQuery('');
    } catch (error) {
      console.error('Query processing error:', error);
      
      // Create error response
      const errorResponse: MockApiResponse = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        category: 'GENERAL',
        status: 'error',
        statusColor: 'red',
        confidence: 0,
        response: error.message === 'Request timeout' 
          ? '⏱️ Request timed out. Please try again with a shorter question.'
          : '🚨 System error occurred. Please try again or contact support.',
        responseKannada: error.message === 'Request timeout'
          ? '⏱️ ವಿನಂತಿ ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಚಿಕ್ಕ ಪ್ರಶ್ನೆಯೊಂದಿಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'
          : '🚨 ಸಿಸ್ಟಮ್ ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬೆಂಬಲವನ್ನು ಸಂಪರ್ಕಿಸಿ.',
        responseHindi: error.message === 'Request timeout'
          ? '⏱️ अनुरोध का समय समाप्त हो गया। कृपया छोटे प्रश्न के साथ पुनः प्रयास करें।'
          : '🚨 सिस्टम त्रुटि हुई। कृपया पुनः प्रयास करें या सहायता से संपर्क करें।',
        icon: error.message === 'Request timeout' ? '⏱️' : '🚨',
        timestamp: new Date().toISOString(),
        metadata: {
          agentType: 'Error Handler',
          actionRequired: true,
          urgency: error.message === 'Request timeout' ? 'medium' : 'high',
          errorType: error.message === 'Request timeout' ? 'timeout' : 'system',
          retryable: true,
          retryAction: () => processQuery(inputQuery)
        }
      };
      
      setResponses(prev => [errorResponse, ...prev]);
      setQuery('');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    processQuery(query);
  };

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery);
    processQuery(sampleQuery);
  };

  const clearHistory = () => {
    setResponses([]);
  };

  const getPlaceholderText = () => {
    const placeholders = {
      en: "Ask about crops, loans, market prices, or security...",
      kn: "ಬೆಳೆಗಳು, ಸಾಲಗಳು, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಅಥವಾ ಭದ್ರತೆಯ ಬಗ್ಗೆ ಕೇಳಿ...",
      hi: "फसलों, ऋण, बाजार की कीमतों या सुरक्षा के बारे में पूछें..."
    };
    return placeholders[language as keyof typeof placeholders] || placeholders.en;
  };

  const getHeaderText = () => {
    const headers = {
      en: "KisaanMitra Mock Query System",
      kn: "ಕಿಸಾನ್‌ಮಿತ್ರ ಮಾಕ್ ಪ್ರಶ್ನೆ ವ್ಯವಸ್ಥೆ",
      hi: "किसानमित्र मॉक क्वेरी सिस्टम"
    };
    return headers[language as keyof typeof headers] || headers.en;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-blue-800">{getHeaderText()}</h2>
          <p className="text-blue-600">
            {language === 'kn' ? 'ಬಣ್ಣ-ಕೋಡೆಡ್ ಸ್ಥಿತಿ ಸೂಚಕಗಳೊಂದಿಗೆ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ' :
             language === 'hi' ? 'रंग-कोडेड स्थिति संकेतकों के साथ कृषि प्रश्नों का परीक्षण करें' :
             'Test agricultural queries with color-coded status indicators'}
          </p>
        </div>
      </Card>

      {/* Query Input */}
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex space-x-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={getPlaceholderText()}
              className="flex-1"
              disabled={isProcessing}
            />
            <Button 
              type="submit" 
              disabled={isProcessing || !query.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
              {isProcessing ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>

          {/* Sample Queries */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">
              {language === 'kn' ? 'ಮಾದರಿ ಪ್ರಶ್ನೆಗಳು:' : 
               language === 'hi' ? 'नमूना प्रश्न:' : 
               'Sample Queries:'}
            </p>
            <div className="flex flex-wrap gap-2">
              {sampleQueries[language as keyof typeof sampleQueries]?.map((sample, index) => (
                <Badge
                  key={index}
                  variant="outline"
                  className="cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  onClick={() => handleSampleQuery(sample)}
                >
                  {sample}
                </Badge>
              ))}
            </div>
          </div>
        </form>
      </Card>

      {/* Response History */}
      {responses.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
              <History className="w-5 h-5" />
              <span>
                {language === 'kn' ? 'ಪ್ರತಿಕ್ರಿಯೆ ಇತಿಹಾಸ' : 
                 language === 'hi' ? 'प्रतिक्रिया इतिहास' : 
                 'Response History'}
              </span>
            </h3>
            <Button
              onClick={clearHistory}
              variant="outline"
              size="sm"
              className="text-gray-600 hover:text-gray-800"
            >
              {language === 'kn' ? 'ಸ್ಪಷ್ಟಗೊಳಿಸಿ' : 
               language === 'hi' ? 'साफ़ करें' : 
               'Clear'}
            </Button>
          </div>

          {/* Status Summary */}
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-3 bg-green-50 border-green-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {responses.filter(r => r.statusColor === 'green').length}
                </div>
                <div className="text-sm text-green-700">
                  {language === 'kn' ? 'ಯಶಸ್ಸು' : language === 'hi' ? 'सफलता' : 'Success'}
                </div>
              </div>
            </Card>
            <Card className="p-3 bg-orange-50 border-orange-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {responses.filter(r => r.statusColor === 'orange').length}
                </div>
                <div className="text-sm text-orange-700">
                  {language === 'kn' ? 'ಎಚ್ಚರಿಕೆ' : language === 'hi' ? 'चेतावनी' : 'Warning'}
                </div>
              </div>
            </Card>
            <Card className="p-3 bg-red-50 border-red-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {responses.filter(r => r.statusColor === 'red').length}
                </div>
                <div className="text-sm text-red-700">
                  {language === 'kn' ? 'ಅಲರ್ಟ್' : language === 'hi' ? 'अलर्ट' : 'Alert'}
                </div>
              </div>
            </Card>
          </div>

          {/* Response List */}
          <div className="space-y-4">
            {responses.map((response) => (
              <StatusIndicator
                key={response.id}
                response={response}
                language={language}
                isProcessing={isProcessing}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MockQueryProcessor;