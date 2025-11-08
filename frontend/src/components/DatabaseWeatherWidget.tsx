
import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { useWeatherData } from '../hooks/useAgriculturalData';
import { Card } from '@/components/ui/card';
import { Droplet, Thermometer, Wind } from 'lucide-react';

export const DatabaseWeatherWidget: React.FC = () => {
  const { translations, currentLanguage } = useLanguage();
  const { data: weatherData, isLoading } = useWeatherData('Bangalore');

  if (isLoading) {
    return (
      <Card className="p-6 bg-gradient-to-r from-blue-400 to-blue-600 text-white">
        <div className="animate-pulse">
          <div className="h-6 bg-blue-300 rounded mb-4"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-16 bg-blue-300 rounded"></div>
            <div className="h-16 bg-blue-300 rounded"></div>
            <div className="h-16 bg-blue-300 rounded"></div>
          </div>
        </div>
      </Card>
    );
  }

  const todayWeather = weatherData?.[0];

  if (!todayWeather) {
    return (
      <Card className="p-6 bg-gradient-to-r from-gray-400 to-gray-600 text-white">
        <p className="text-center">
          {currentLanguage === 'kannada' ? 'ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ' : 'Weather data not available'}
        </p>
      </Card>
    );
  }

  const getWeatherIcon = (condition: string) => {
    switch (condition) {
      case 'sunny': return '☀️';
      case 'partly_cloudy': return '⛅';
      case 'cloudy': return '☁️';
      case 'light_rain': return '🌦️';
      case 'rainy': return '🌧️';
      default: return '⛅';
    }
  };

  const getWeatherText = (condition: string) => {
    const conditions = {
      sunny: currentLanguage === 'kannada' ? 'ಬಿಸಿಲು' : 'Sunny',
      partly_cloudy: currentLanguage === 'kannada' ? 'ಅರೆ ಮೋಡ' : 'Partly Cloudy',
      cloudy: currentLanguage === 'kannada' ? 'ಮೋಡ' : 'Cloudy',
      light_rain: currentLanguage === 'kannada' ? 'ಸಣ್ಣ ಮಳೆ' : 'Light Rain',
      rainy: currentLanguage === 'kannada' ? 'ಮಳೆ' : 'Rainy'
    };
    return conditions[condition as keyof typeof conditions] || condition;
  };

  return (
    <Card className="p-6 bg-gradient-to-r from-blue-400 to-blue-600 text-white shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">{translations.todaysWeather}</h2>
        <div className="text-4xl">
          {getWeatherIcon(todayWeather.weather_condition || 'partly_cloudy')}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <Thermometer size={20} />
            <span className="text-2xl font-bold">{todayWeather.temperature}°C</span>
          </div>
          <p className="text-blue-100 text-sm">
            {translations.temperature}
          </p>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <Droplet size={20} />
            <span className="text-2xl font-bold">{todayWeather.humidity}%</span>
          </div>
          <p className="text-blue-100 text-sm">
            {translations.humidity}
          </p>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <Wind size={20} />
            <span className="text-2xl font-bold">{todayWeather.wind_speed}km/h</span>
          </div>
          <p className="text-blue-100 text-sm">
            {currentLanguage === 'kannada' ? 'ಗಾಳಿ' : 'Wind'}
          </p>
        </div>
      </div>

      <div className="mt-4 p-3 bg-white/20 rounded-lg">
        <p className="text-center font-medium">
          {getWeatherText(todayWeather.weather_condition || 'partly_cloudy')} - {translations.goodForFarming}
        </p>
        {todayWeather.rainfall && todayWeather.rainfall > 0 && (
          <p className="text-center text-sm mt-1">
            {translations.rainfall}: {todayWeather.rainfall}mm
          </p>
        )}
      </div>
    </Card>
  );
};
