
import React, { useState, useEffect } from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { Sun, Droplet } from 'lucide-react';

export const WeatherWidget: React.FC = () => {
  const { translations, currentLanguage } = useLanguage();
  const [weather, setWeather] = useState({
    temperature: 28,
    humidity: 65,
    rainfall: 12,
    condition: 'partly_cloudy'
  });

  const getWeatherIcon = (condition: string) => {
    switch (condition) {
      case 'sunny': return '☀️';
      case 'partly_cloudy': return '⛅';
      case 'cloudy': return '☁️';
      case 'rainy': return '🌧️';
      default: return '⛅';
    }
  };

  const getWeatherText = (condition: string) => {
    const conditions = {
      sunny: currentLanguage === 'kannada' ? 'ಬಿಸಿಲು' : 'Sunny',
      partly_cloudy: currentLanguage === 'kannada' ? 'ಅರೆ ಮೋಡ' : 'Partly Cloudy',
      cloudy: currentLanguage === 'kannada' ? 'ಮೋಡ' : 'Cloudy',
      rainy: currentLanguage === 'kannada' ? 'ಮಳೆ' : 'Rainy'
    };
    return conditions[condition as keyof typeof conditions] || condition;
  };

  return (
    <div className="bg-gradient-to-r from-blue-400 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">{translations.todaysWeather}</h2>
        <div className="text-4xl">
          {getWeatherIcon(weather.condition)}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-3xl font-bold">{weather.temperature}°C</div>
          <p className="text-blue-100 text-sm">
            {translations.temperature}
          </p>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center space-x-1">
            <Droplet size={20} />
            <span className="text-2xl font-bold">{weather.humidity}%</span>
          </div>
          <p className="text-blue-100 text-sm">
            {translations.humidity}
          </p>
        </div>

        <div className="text-center">
          <div className="text-2xl font-bold">{weather.rainfall}mm</div>
          <p className="text-blue-100 text-sm">
            {translations.rainfall}
          </p>
        </div>
      </div>

      <div className="mt-4 p-3 bg-white/20 rounded-lg">
        <p className="text-center font-medium">
          {getWeatherText(weather.condition)} - {translations.goodForFarming}
        </p>
      </div>
    </div>
  );
};
