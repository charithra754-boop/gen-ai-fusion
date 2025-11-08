
import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { Wheat } from 'lucide-react';

interface Recommendation {
  crop: string;
  confidence: number;
  season: string;
  profitability: string;
}

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const { translations, currentLanguage } = useLanguage();

  const getCropName = (crop: string) => {
    const cropNames = {
      wheat: currentLanguage === 'kannada' ? 'ಗೋಧಿ' : 'Wheat',
      rice: currentLanguage === 'kannada' ? 'ಅಕ್ಕಿ' : 'Rice',
      corn: currentLanguage === 'kannada' ? 'ಜೋಳ' : 'Corn'
    };
    return cropNames[crop as keyof typeof cropNames] || crop;
  };

  const getProfitabilityColor = (profitability: string) => {
    switch (profitability) {
      case 'very_high': return 'text-green-600 bg-green-100';
      case 'high': return 'text-green-500 bg-green-50';
      case 'medium': return 'text-yellow-500 bg-yellow-50';
      case 'low': return 'text-red-500 bg-red-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getProfitabilityText = (profitability: string) => {
    const texts = {
      very_high: currentLanguage === 'kannada' ? 'ಅತಿ ಲಾಭದಾಯಕ' : 'Very Profitable',
      high: currentLanguage === 'kannada' ? 'ಲಾಭದಾಯಕ' : 'Profitable',
      medium: currentLanguage === 'kannada' ? 'ಸಾಧಾರಣ' : 'Moderate',
      low: currentLanguage === 'kannada' ? 'ಕಡಿಮೆ ಲಾಭ' : 'Low Profit'
    };
    return texts[profitability as keyof typeof texts] || profitability;
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-xl border-l-4 border-green-500">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">
          {translations.recommendedCrop}
        </h2>
        <div className="flex items-center space-x-2">
          <Wheat className="text-green-600" size={32} />
          <span className="text-3xl font-bold text-green-600">
            {recommendation.confidence}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-2">
            <Wheat size={32} className="text-green-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-800">
            {getCropName(recommendation.crop)}
          </h3>
          <p className="text-gray-600 text-sm">
            {translations.recommendedFor} {recommendation.season}
          </p>
        </div>

        <div className="text-center">
          <div className="text-4xl mb-2">💰</div>
          <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getProfitabilityColor(recommendation.profitability)}`}>
            {getProfitabilityText(recommendation.profitability)}
          </div>
        </div>

        <div className="text-center">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-gray-600 text-sm">
            {translations.confidence}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${recommendation.confidence}%` }}
            />
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-green-50 rounded-lg">
        <p className="text-green-800 font-medium text-center">
          {currentLanguage === 'kannada' 
            ? 'ಈ ಬೆಳೆ ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ಸೂಕ್ತವಾಗಿದೆ'
            : 'This crop is suitable for current weather and soil conditions'
          }
        </p>
      </div>
    </div>
  );
};
