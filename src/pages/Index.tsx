
import React, { useState } from 'react';
import { SmartAIAssistant } from '../components/SmartAIAssistant';
import { DatabaseWeatherWidget } from '../components/DatabaseWeatherWidget';
import { DatabaseCropRecommendations } from '../components/DatabaseCropRecommendations';
import { NavigationGrid } from '../components/NavigationGrid';
import { LanguageSelector } from '../components/LanguageSelector';
import { useLanguage } from '../hooks/useLanguage';
import { useFarmingTips } from '../hooks/useAgriculturalData';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Wheat, Droplet, Sun, Lightbulb, TestTube } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Index = () => {
  const { currentLanguage, translations } = useLanguage();
  const { data: farmingTips } = useFarmingTips();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-blue-50">
      {/* Header with Language Selector */}
      <div className="bg-white shadow-sm p-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Wheat className="text-green-600" size={32} />
          <h1 className="text-2xl font-bold text-green-800">AgroMind</h1>
          <span className="text-sm text-green-600 bg-green-100 px-2 py-1 rounded-full">
            {currentLanguage === 'kannada' ? 'AI ಚಾಲಿತ' : 'AI Powered'}
          </span>
        </div>
        <LanguageSelector />
      </div>

      {/* Main Content */}
      <div className="container mx-auto p-4 space-y-6">
        {/* Smart AI Assistant - Central Feature */}
        <SmartAIAssistant currentLanguage={currentLanguage} />

        {/* Soil Analysis CTA */}
        <Card className="p-6 bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-amber-100 rounded-lg">
                <TestTube className="text-amber-600" size={32} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">
                  {currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ' : 'Soil Analysis'}
                </h2>
                <p className="text-gray-600">
                  {currentLanguage === 'kannada' 
                    ? 'ನಿಮ್ಮ ಮಣ್ಣಿಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಯನ್ನು AI ಮೂಲಕ ಪತ್ತೆ ಮಾಡಿ' 
                    : 'Get AI-powered crop recommendations based on your soil parameters'
                  }
                </p>
              </div>
            </div>
            <Button
              onClick={() => navigate('/soil-analysis')}
              className="bg-amber-600 hover:bg-amber-700 text-white"
            >
              {currentLanguage === 'kannada' ? 'ಪರೀಕ್ಷೆ ಮಾಡಿ' : 'Test Now'}
            </Button>
          </div>
        </Card>

        {/* Weather and Crop Recommendations Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DatabaseWeatherWidget />
          <DatabaseCropRecommendations />
        </div>

        {/* Farming Tips Section */}
        {farmingTips && farmingTips.length > 0 && (
          <Card className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Lightbulb className="text-yellow-600" size={24} />
              <h2 className="text-xl font-bold text-gray-800">
                {currentLanguage === 'kannada' ? 'ಇಂದಿನ ಕೃಷಿ ಸಲಹೆಗಳು' : 'Today\'s Farming Tips'}
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {farmingTips.slice(0, 3).map((tip) => (
                <Card key={tip.id} className="p-4 bg-yellow-50 border-yellow-200">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-yellow-100 rounded-lg flex-shrink-0">
                      <Lightbulb className="text-yellow-600" size={16} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800 mb-2">
                        {currentLanguage === 'kannada' ? tip.tip_title_kannada : tip.tip_title}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {currentLanguage === 'kannada' ? tip.tip_content_kannada : tip.tip_content}
                      </p>
                      <div className="mt-2">
                        <span className="inline-block bg-yellow-200 text-yellow-800 text-xs px-2 py-1 rounded-full">
                          {tip.category.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        )}

        {/* Navigation Grid */}
        <NavigationGrid />

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Wheat className="text-green-600" size={24} />
              </div>
              <h3 className="text-lg font-semibold text-gray-800">
                {translations.cropAdvice}
              </h3>
            </div>
            <p className="text-gray-600 text-sm">
              {translations.cropAdviceDesc}
            </p>
          </Card>

          <Card className="p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Droplet className="text-blue-600" size={24} />
              </div>
              <h3 className="text-lg font-semibold text-gray-800">
                {translations.waterManagement}
              </h3>
            </div>
            <p className="text-gray-600 text-sm">
              {translations.waterManagementDesc}
            </p>
          </Card>

          <Card className="p-6 hover:shadow-xl transition-shadow cursor-pointer">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Sun className="text-yellow-600" size={24} />
              </div>
              <h3 className="text-lg font-semibold text-gray-800">
                {translations.weather}
              </h3>
            </div>
            <p className="text-gray-600 text-sm">
              {translations.weatherDesc}
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Index;
