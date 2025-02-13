import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  description: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, description }) => {
  // Format number values
  const formattedValue = typeof value === 'number' 
    ? value >= 1000000
      ? `${(value / 1000000).toFixed(2)}M`
      : value >= 1000
      ? `${(value / 1000).toFixed(1)}k`
      : value.toLocaleString()
    : value;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 transition-all duration-200 hover:shadow-lg">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
        {title}
      </h3>
      <div className="flex items-baseline">
        <p className="text-2xl font-semibold text-gray-900">
          {formattedValue}
        </p>
      </div>
      <p className="mt-2 text-sm text-gray-600">
        {description}
      </p>
    </div>
  );
}; 