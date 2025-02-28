import React from 'react';
import type { FC } from 'react';

export interface MetricCardProps {
  title: string;
  value: string | number;
  description: string;
  globalValue?: number;
  trend?: number;
  unit?: string;
}

export const MetricCard: FC<MetricCardProps> = ({ 
  title, 
  value, 
  description, 
  globalValue, 
  trend,
  unit = '%'
}) => {
  const formatNumberValue = (val: number): string => {
    if (val >= 1000000) return `${(val / 1000000).toFixed(2)}M`;
    if (val >= 1000) return `${(val / 1000).toFixed(1)}k`;
    return val.toLocaleString();
  };

  // Format number values
  const formattedValue = typeof value === 'number' 
    ? formatNumberValue(value)
    : value;

  // Calculate difference from global
  const difference = typeof value === 'number' && globalValue 
    ? ((value - globalValue) / globalValue * 100).toFixed(1)
    : null;

  // Determine if the difference is positive or negative
  const isDifferencePositive: boolean = Boolean(difference && parseFloat(difference) > 0);
  const isDifferenceNegative: boolean = Boolean(difference && parseFloat(difference) < 0);

  // Determine if the trend is positive or negative
  const isTrendPositive: boolean = Boolean(trend && trend > 0);
  const isTrendNegative: boolean = Boolean(trend && trend < 0);

  const getColorClass = (isPositive: boolean, isNegative: boolean): string => {
    if (isPositive) return 'text-green-600';
    if (isNegative) return 'text-red-600';
    return 'text-gray-600';
  };

  const getTrendArrow = (isPositive: boolean, isNegative: boolean): string => {
    if (isPositive) return '↗';
    if (isNegative) return '↘';
    return '→';
  };

  const getDifferenceArrow = (isPositive: boolean, isNegative: boolean): string => {
    if (isPositive) return '↑';
    if (isNegative) return '↓';
    return '';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 transition-all duration-200 hover:shadow-lg">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
        {title}
      </h3>
      <div className="flex items-baseline justify-between">
        <div className="flex items-baseline space-x-2">
          <p className="text-2xl font-semibold text-gray-900">
            {formattedValue}{unit && ` ${unit}`}
          </p>
          {difference && (
            <span className={`text-sm font-medium ${getColorClass(isDifferencePositive, isDifferenceNegative)}`}>
              {getDifferenceArrow(isDifferencePositive, isDifferenceNegative)} {Math.abs(parseFloat(difference))}%
            </span>
          )}
        </div>
        {trend !== undefined && (
          <div className={`flex items-center ${getColorClass(isTrendPositive, isTrendNegative)}`}>
            {getTrendArrow(isTrendPositive, isTrendNegative)}
            <span className="text-sm ml-1">{Math.abs(trend).toFixed(1)}%</span>
          </div>
        )}
      </div>
      <p className="mt-2 text-sm text-gray-600">
        {description}
      </p>
      {globalValue !== undefined && (
        <p className="mt-1 text-sm text-gray-500">
          vs global {globalValue.toFixed(1)}{unit}
        </p>
      )}
    </div>
  );
};