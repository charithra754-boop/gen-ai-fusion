
import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import { useLanguage } from '../hooks/useLanguage';
import { useSoilAnalysis } from '../hooks/useAgriculturalData';
import { Sprout, TestTube, Target, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export const SoilAnalysisForm: React.FC = () => {
  const { currentLanguage } = useLanguage();
  const { predictCrop } = useSoilAnalysis();
  
  const [soilData, setSoilData] = useState({
    nitrogen: 50,
    phosphorus: 50,
    potassium: 50,
    temperature: 25,
    humidity: 60,
    ph: 6.5,
    rainfall: 800
  });
  
  const [prediction, setPrediction] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await predictCrop.mutateAsync({
        ...soilData,
        location: 'Karnataka'
      });
      setPrediction(result);
      toast.success(currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಪೂರ್ಣಗೊಂಡಿದೆ!' : 'Soil analysis completed!');
    } catch (error) {
      toast.error(currentLanguage === 'kannada' ? 'ದೋಷ ಸಂಭವಿಸಿದೆ' : 'Analysis failed');
    }
    setIsAnalyzing(false);
  };

  const getParameterInfo = (param: string) => {
    const info = {
      nitrogen: {
        en: 'Nitrogen (N) - Essential for plant growth and leaf development',
        kn: 'ನೈಟ್ರೋಜನ್ (N) - ಸಸ್ಯಗಳ ಬೆಳವಣಿಗೆ ಮತ್ತು ಎಲೆಗಳ ಬೆಳವಣಿಗೆಗೆ ಅಗತ್ಯ'
      },
      phosphorus: {
        en: 'Phosphorus (P) - Important for root development and flowering',
        kn: 'ಫಾಸ್ಫರಸ್ (P) - ಬೇರುಗಳ ಬೆಳವಣಿಗೆ ಮತ್ತು ಹೂಬಿಡುವಿಕೆಗೆ ಮುಖ್ಯ'
      },
      potassium: {
        en: 'Potassium (K) - Helps in disease resistance and fruit quality',
        kn: 'ಪೊಟ್ಯಾಸಿಯಮ್ (K) - ರೋಗ ಪ್ರತಿರೋಧ ಮತ್ತು ಹಣ್ಣಿನ ಗುಣಮಟ್ಟಕ್ಕೆ ಸಹಾಯ'
      }
    };
    return info[param as keyof typeof info]?.[currentLanguage as keyof typeof info.nitrogen] || '';
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <TestTube className="text-green-600" size={32} />
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ' : 'Soil Analysis'}
            </h2>
            <p className="text-gray-600">
              {currentLanguage === 'kannada' 
                ? 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಮಾಹಿತಿ ನಮೂದಿಸಿ ಮತ್ತು ಯಾವ ಬೆಳೆ ಬೆಳೆಸಬೇಕೆಂದು ತಿಳಿಯಿರಿ' 
                : 'Enter your soil parameters to get crop recommendations'
              }
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* NPK Values */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center space-x-2">
              <Sprout size={20} />
              <span>{currentLanguage === 'kannada' ? 'ಪೋಷಕಾಂಶಗಳು (NPK)' : 'Nutrients (NPK)'}</span>
            </h3>
            
            {/* Nitrogen */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ನೈಟ್ರೋಜನ್ (N)' : 'Nitrogen (N)'}: {soilData.nitrogen} mg/kg
              </label>
              <Slider
                value={[soilData.nitrogen]}
                onValueChange={(value) => setSoilData({...soilData, nitrogen: value[0]})}
                max={200}
                min={0}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">{getParameterInfo('nitrogen')}</p>
            </div>

            {/* Phosphorus */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ಫಾಸ್ಫರಸ್ (P)' : 'Phosphorus (P)'}: {soilData.phosphorus} mg/kg
              </label>
              <Slider
                value={[soilData.phosphorus]}
                onValueChange={(value) => setSoilData({...soilData, phosphorus: value[0]})}
                max={150}
                min={0}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">{getParameterInfo('phosphorus')}</p>
            </div>

            {/* Potassium */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ಪೊಟ್ಯಾಸಿಯಮ್ (K)' : 'Potassium (K)'}: {soilData.potassium} mg/kg
              </label>
              <Slider
                value={[soilData.potassium]}
                onValueChange={(value) => setSoilData({...soilData, potassium: value[0]})}
                max={300}
                min={0}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">{getParameterInfo('potassium')}</p>
            </div>
          </div>

          {/* Environmental Factors */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-700">
              {currentLanguage === 'kannada' ? 'ಪರಿಸರ ಅಂಶಗಳು' : 'Environmental Factors'}
            </h3>
            
            {/* Temperature */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ತಾಪಮಾನ' : 'Temperature'}: {soilData.temperature}°C
              </label>
              <Slider
                value={[soilData.temperature]}
                onValueChange={(value) => setSoilData({...soilData, temperature: value[0]})}
                max={45}
                min={5}
                step={0.5}
                className="w-full"
              />
            </div>

            {/* Humidity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ಆರ್ದ್ರತೆ' : 'Humidity'}: {soilData.humidity}%
              </label>
              <Slider
                value={[soilData.humidity]}
                onValueChange={(value) => setSoilData({...soilData, humidity: value[0]})}
                max={100}
                min={0}
                step={1}
                className="w-full"
              />
            </div>

            {/* pH */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'pH ಮಟ್ಟ' : 'pH Level'}: {soilData.ph}
              </label>
              <Slider
                value={[soilData.ph]}
                onValueChange={(value) => setSoilData({...soilData, ph: value[0]})}
                max={14}
                min={0}
                step={0.1}
                className="w-full"
              />
            </div>

            {/* Rainfall */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentLanguage === 'kannada' ? 'ಮಳೆ' : 'Rainfall'}: {soilData.rainfall} mm
              </label>
              <Slider
                value={[soilData.rainfall]}
                onValueChange={(value) => setSoilData({...soilData, rainfall: value[0]})}
                max={3000}
                min={0}
                step={10}
                className="w-full"
              />
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            size="lg"
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3"
          >
            {isAnalyzing ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{currentLanguage === 'kannada' ? 'ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...' : 'Analyzing...'}</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Target size={20} />
                <span>{currentLanguage === 'kannada' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಮಾಡಿ' : 'Analyze Soil'}</span>
              </div>
            )}
          </Button>
        </div>
      </Card>

      {/* Results Display */}
      {prediction && (
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <TrendingUp className="text-green-600" size={32} />
              <h3 className="text-2xl font-bold text-green-800">
                {currentLanguage === 'kannada' ? 'ಸಲಹೆ ಫಲಿತಾಂಶ' : 'Recommendation Result'}
              </h3>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-center mb-4">
                <h4 className="text-xl font-semibold text-gray-800 mb-2">
                  {currentLanguage === 'kannada' ? 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ:' : 'Recommended Crop:'}
                </h4>
                <p className="text-3xl font-bold text-green-600">{prediction.predicted_crop}</p>
                {prediction.confidence_score && (
                  <p className="text-lg text-gray-600 mt-2">
                    {currentLanguage === 'kannada' ? 'ವಿಶ್ವಾಸಾರ್ಹತೆ:' : 'Confidence:'} {prediction.confidence_score}%
                  </p>
                )}
              </div>
              
              {prediction.alternative_crops && (
                <div className="mt-4">
                  <h5 className="font-semibold text-gray-700 mb-2">
                    {currentLanguage === 'kannada' ? 'ಇತರ ಆಯ್ಕೆಗಳು:' : 'Alternative Options:'}
                  </h5>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {prediction.alternative_crops.map((crop: string, index: number) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {crop}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
