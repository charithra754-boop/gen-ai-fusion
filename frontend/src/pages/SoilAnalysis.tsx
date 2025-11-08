
import React from 'react';
import { SoilAnalysisForm } from '../components/SoilAnalysisForm';
import { LanguageSelector } from '../components/LanguageSelector';
import { useLanguage } from '../hooks/useLanguage';
import { Button } from '@/components/ui/button';
import { ArrowLeft, TestTube } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const SoilAnalysis = () => {
  const { currentLanguage } = useLanguage();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft size={20} />
            <span>{currentLanguage === 'kannada' ? 'ಮನೆಗೆ' : currentLanguage === 'hindi' ? 'घर' : 'Home'}</span>
          </Button>
          <div className="flex items-center space-x-2">
            <TestTube className="text-amber-600" size={32} />
            <div>
              <h1 className="text-2xl font-bold text-green-800">
                {currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಮತ್ತು ಬೆಳೆ ಯೋಜನೆ' : currentLanguage === 'hindi' ? 'मिट्टी परीक्षण और फसल योजना' : 'Soil Analysis & Crop Portfolio'}
              </h1>
              <p className="text-xs text-gray-600">
                {currentLanguage === 'kannada' ? 'GAA - ಜಿಯೋ-ಅಗ್ರೋನಮಿ ಏಜೆಂಟ್' : currentLanguage === 'hindi' ? 'GAA - भू-कृषि एजेंट' : 'GAA - Geo-Agronomy Agent'}
              </p>
            </div>
          </div>
        </div>
        <LanguageSelector />
      </div>

      {/* Main Content */}
      <div className="container mx-auto p-4">
        <SoilAnalysisForm />
      </div>
    </div>
  );
};

export default SoilAnalysis;
