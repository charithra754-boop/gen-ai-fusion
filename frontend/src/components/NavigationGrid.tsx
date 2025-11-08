
import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { Wheat, Droplet, Sun } from 'lucide-react';

export const NavigationGrid: React.FC = () => {
  const { translations } = useLanguage();

  const navigationItems = [
    {
      icon: <Wheat size={48} className="text-green-600" />,
      title: translations.cropRecommendations,
      description: translations.cropRecommendationsDesc,
      color: 'bg-green-100',
      action: () => console.log('Crop recommendations clicked')
    },
    {
      icon: <Droplet size={48} className="text-blue-600" />,
      title: translations.irrigation,
      description: translations.irrigationDesc,
      color: 'bg-blue-100',
      action: () => console.log('Irrigation clicked')
    },
    {
      icon: <Sun size={48} className="text-yellow-600" />,
      title: translations.weatherForecast,
      description: translations.weatherForecastDesc,
      color: 'bg-yellow-100',
      action: () => console.log('Weather clicked')
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {navigationItems.map((item, index) => (
        <div
          key={index}
          onClick={item.action}
          className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105"
        >
          <div className={`${item.color} rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4`}>
            {item.icon}
          </div>
          <h3 className="text-xl font-bold text-gray-800 text-center mb-2">
            {item.title}
          </h3>
          <p className="text-gray-600 text-center text-sm">
            {item.description}
          </p>
        </div>
      ))}
    </div>
  );
};
