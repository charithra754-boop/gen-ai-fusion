import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertTriangle, CheckCircle, XCircle, Shield, TrendingUp, Sprout, CreditCard, HelpCircle, RefreshCw } from 'lucide-react';
import { MockApiResponse } from '../lib/mockApiSystem';

interface StatusIndicatorProps {
  response: MockApiResponse;
  language?: string;
  isProcessing?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ response, language = 'en', isProcessing = false }) => {
  const getStatusIcon = () => {
    switch (response.status) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-orange-600" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-600" />;
      default:
        return <HelpCircle className="w-6 h-6 text-gray-600" />;
    }
  };

  const getCategoryIcon = () => {
    switch (response.category) {
      case 'PIN':
        return <Shield className="w-5 h-5" />;
      case 'KCC':
        return <CreditCard className="w-5 h-5" />;
      case 'STRESS':
        return <Sprout className="w-5 h-5" />;
      case 'SELL':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <HelpCircle className="w-5 h-5" />;
    }
  };

  const getBackgroundColor = () => {
    switch (response.statusColor) {
      case 'green':
        return 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200';
      case 'orange':
        return 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200';
      case 'red':
        return 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200';
      default:
        return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200';
    }
  };

  const getStatusText = () => {
    const statusTexts = {
      success: {
        en: 'Success',
        kn: 'ಯಶಸ್ಸು',
        hi: 'सफलता'
      },
      warning: {
        en: 'Warning',
        kn: 'ಎಚ್ಚರಿಕೆ',
        hi: 'चेतावनी'
      },
      error: {
        en: 'Alert',
        kn: 'ಅಲರ್ಟ್',
        hi: 'अलर्ट'
      }
    };
    
    return statusTexts[response.status]?.[language as keyof typeof statusTexts.success] || statusTexts[response.status]?.en;
  };

  const getCategoryText = () => {
    const categoryTexts = {
      PIN: {
        en: 'Security',
        kn: 'ಭದ್ರತೆ',
        hi: 'सुरक्षा'
      },
      KCC: {
        en: 'Credit',
        kn: 'ಕ್ರೆಡಿಟ್',
        hi: 'क्रेडिट'
      },
      STRESS: {
        en: 'Crop Health',
        kn: 'ಬೆಳೆ ಆರೋಗ್ಯ',
        hi: 'फसल स्वास्थ्य'
      },
      SELL: {
        en: 'Market',
        kn: 'ಮಾರುಕಟ್ಟೆ',
        hi: 'बाजार'
      },
      GENERAL: {
        en: 'General',
        kn: 'ಸಾಮಾನ್ಯ',
        hi: 'सामान्य'
      }
    };
    
    return categoryTexts[response.category]?.[language as keyof typeof categoryTexts.PIN] || categoryTexts[response.category]?.en;
  };

  return (
    <Card className={`p-4 ${getBackgroundColor()} transition-all duration-300 hover:shadow-lg`}>
      {/* Header with Status and Category */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <Badge 
            variant="outline" 
            className={`
              ${response.statusColor === 'green' ? 'border-green-300 text-green-700 bg-green-100' : ''}
              ${response.statusColor === 'orange' ? 'border-orange-300 text-orange-700 bg-orange-100' : ''}
              ${response.statusColor === 'red' ? 'border-red-300 text-red-700 bg-red-100' : ''}
            `}
          >
            {getStatusText()}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          {getCategoryIcon()}
          <span>{getCategoryText()}</span>
        </div>
      </div>

      {/* Response Content */}
      <div className="space-y-3">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{response.icon}</span>
          <div className="flex-1">
            <p className={`
              font-medium leading-relaxed
              ${response.statusColor === 'green' ? 'text-green-800' : ''}
              ${response.statusColor === 'orange' ? 'text-orange-800' : ''}
              ${response.statusColor === 'red' ? 'text-red-800' : ''}
            `}>
              {language === 'kn' ? response.responseKannada : 
               language === 'hi' ? response.responseHindi : 
               response.response}
            </p>
          </div>
        </div>

        {/* Error Actions */}
        {response.status === 'error' && response.metadata?.retryable && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              <Button
                onClick={() => response.metadata?.retryAction?.()}
                variant="outline"
                size="sm"
                className="bg-blue-50 text-blue-700 border-blue-300 hover:bg-blue-100"
                disabled={isProcessing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isProcessing ? 'animate-spin' : ''}`} />
                {language === 'kn' ? 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ' : language === 'hi' ? 'पुनः प्रयास करें' : 'Try Again'}
              </Button>
              
              {response.metadata?.errorType === 'timeout' && (
                <span className="text-xs text-gray-600">
                  💡 {language === 'kn' ? 'ಸಲಹೆ: ಚಿಕ್ಕ, ಹೆಚ್ಚು ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಯನ್ನು ಪ್ರಯತ್ನಿಸಿ' : 
                        language === 'hi' ? 'सुझाव: छोटा, अधिक विशिष्ट प्रश्न आज़माएं' : 
                        'Tip: Try a shorter, more specific question'}
                </span>
              )}
              
              {response.metadata?.errorType === 'validation' && (
                <span className="text-xs text-gray-600">
                  💡 {language === 'kn' ? 'ಸಲಹೆ: ಬೆಳೆಗಳು, ಸಾಲಗಳು, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಅಥವಾ ಭದ್ರತೆಯ ಬಗ್ಗೆ ಕೇಳಿ' : 
                        language === 'hi' ? 'सुझाव: फसलों, ऋण, बाजार की कीमतों या सुरक्षा के बारे में पूछें' : 
                        'Tip: Ask about crops, loans, market prices, or security'}
                </span>
              )}
              
              {response.metadata?.errorType === 'system' && (
                <span className="text-xs text-gray-600">
                  💡 {language === 'kn' ? 'ತುರ್ತು ಸಹಾಯವಾಣಿ: 1551 (ಕೃಷಿ ಬೆಂಬಲ)' : 
                        language === 'hi' ? 'आपातकालीन हेल्पलाइन: 1551 (कृषि सहायता)' : 
                        'Emergency helpline: 1551 (Agricultural support)'}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-200 space-y-1 sm:space-y-0">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4">
            <span>
              {language === 'kn' ? 'ಏಜೆಂಟ್:' : language === 'hi' ? 'एजेंट:' : 'Agent:'} {response.metadata?.agentType}
            </span>
            <span>
              {language === 'kn' ? 'ವಿಶ್ವಾಸ:' : language === 'hi' ? 'विश्वास:' : 'Confidence:'} {response.confidence}%
            </span>
            <span>{new Date(response.timestamp).toLocaleString()}</span>
            {response.metadata?.errorType && (
              <span className="text-red-600">
                {language === 'kn' ? 'ದೋಷ:' : language === 'hi' ? 'त्रुटि:' : 'Error:'} {response.metadata.errorType}
              </span>
            )}
          </div>
          
          {response.metadata?.actionRequired && (
            <Badge 
              variant="outline" 
              className={`
                text-xs
                ${response.metadata.urgency === 'high' ? 'border-red-300 text-red-600 bg-red-50' : ''}
                ${response.metadata.urgency === 'medium' ? 'border-orange-300 text-orange-600 bg-orange-50' : ''}
                ${response.metadata.urgency === 'low' ? 'border-blue-300 text-blue-600 bg-blue-50' : ''}
              `}
            >
              {language === 'kn' ? 'ಕ್ರಮ ಅಗತ್ಯ' : language === 'hi' ? 'कार्रवाई आवश्यक' : 'Action Required'}
            </Badge>
          )}
        </div>
      </div>
    </Card>
  );
};

export default StatusIndicator;