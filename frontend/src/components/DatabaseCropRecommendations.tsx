
import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { useCropRecommendations } from '../hooks/useAgriculturalData';
import { Card } from '@/components/ui/card';
import { Wheat, TrendingUp, Calendar, MapPin } from 'lucide-react';

export const DatabaseCropRecommendations: React.FC = () => {
  const { translations, currentLanguage } = useLanguage();
  const { data: cropRecommendations, isLoading } = useCropRecommendations('Karnataka');

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Card>
    );
  }

  if (!cropRecommendations || cropRecommendations.length === 0) {
    return (
      <Card className="p-6">
        <p className="text-center text-gray-500">
          {currentLanguage === 'kannada' ? 'ಬೆಳೆ ಶಿಫಾರಸುಗಳು ಲಭ್ಯವಿಲ್ಲ' : 'No crop recommendations available'}
        </p>
      </Card>
    );
  }

  const getCropNameKannada = (cropName: string) => {
    const kannadaNames: { [key: string]: string } = {
      'Rice': 'ಅಕ್ಕಿ',
      'Wheat': 'ಗೋಧಿ',
      'Sugarcane': 'ಕಬ್ಬು',
      'Cotton': 'ಹತ್ತಿ',
      'Maize': 'ಜೋಳ'
    };
    return kannadaNames[cropName] || cropName;
  };

  const getSeasonKannada = (season: string) => {
    const kannadaSeasons: { [key: string]: string } = {
      'monsoon': 'ಮಳೆಗಾಲ',
      'winter': 'ಚಳಿಗಾಲ',
      'summer': 'ಬೇಸಿಗೆ',
      'kharif': 'ಖರೀಫ್',
      'year_round': 'ವರ್ಷಪೂರ್ಣ'
    };
    return kannadaSeasons[season] || season;
  };

  const getProfitabilityColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <Card className="p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Wheat className="text-green-600" size={24} />
        <h2 className="text-xl font-bold text-gray-800">
          {translations.cropRecommendations}
        </h2>
      </div>

      <div className="space-y-4">
        {cropRecommendations.slice(0, 3).map((crop, index) => (
          <Card key={crop.id} className={`p-4 border-l-4 ${index === 0 ? 'border-green-500 bg-green-50' : 'border-gray-300'}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${index === 0 ? 'bg-green-100' : 'bg-gray-100'}`}>
                  <Wheat className={index === 0 ? 'text-green-600' : 'text-gray-600'} size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-gray-800">
                    {currentLanguage === 'kannada' ? getCropNameKannada(crop.crop_name) : crop.crop_name}
                  </h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Calendar size={14} />
                    <span>{currentLanguage === 'kannada' ? getSeasonKannada(crop.season) : crop.season}</span>
                    {crop.region && (
                      <>
                        <MapPin size={14} />
                        <span>{crop.region}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-sm font-semibold ${getProfitabilityColor(crop.profitability_score || 0)}`}>
                  <TrendingUp size={14} />
                  <span>{crop.profitability_score}%</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              {crop.growing_duration && (
                <div className="flex flex-col">
                  <span className="text-gray-500">
                    {currentLanguage === 'kannada' ? 'ಬೆಳವಣಿಗೆ ಅವಧಿ' : 'Duration'}
                  </span>
                  <span className="font-semibold">{crop.growing_duration} days</span>
                </div>
              )}
              {crop.rainfall_required && (
                <div className="flex flex-col">
                  <span className="text-gray-500">
                    {currentLanguage === 'kannada' ? 'ಮಳೆ ಅಗತ್ಯ' : 'Rainfall'}
                  </span>
                  <span className="font-semibold">{crop.rainfall_required}mm</span>
                </div>
              )}
              {crop.temperature_min && crop.temperature_max && (
                <div className="flex flex-col">
                  <span className="text-gray-500">
                    {currentLanguage === 'kannada' ? 'ತಾಪಮಾನ' : 'Temperature'}
                  </span>
                  <span className="font-semibold">{crop.temperature_min}-{crop.temperature_max}°C</span>
                </div>
              )}
              {crop.soil_type && (
                <div className="flex flex-col">
                  <span className="text-gray-500">
                    {currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪ್ರಕಾರ' : 'Soil Type'}
                  </span>
                  <span className="font-semibold">{crop.soil_type}</span>
                </div>
              )}
            </div>

            {index === 0 && (
              <div className="mt-3 p-2 bg-green-100 rounded-lg">
                <p className="text-green-800 text-sm font-medium text-center">
                  {currentLanguage === 'kannada' 
                    ? '🏆 ಅತ್ಯುತ್ತಮ ಶಿಫಾರಸು - ಅತಿ ಲಾಭದಾಯಕ!' 
                    : '🏆 Top Recommendation - Most Profitable!'
                  }
                </p>
              </div>
            )}
          </Card>
        ))}
      </div>
    </Card>
  );
};
