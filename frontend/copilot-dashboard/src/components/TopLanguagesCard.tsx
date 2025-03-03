import React from 'react';
import { LanguageData } from '@/hooks/useLanguageData';

interface TopLanguagesCardProps {
  languages: LanguageData[];
  loading: boolean;
  error: string | null;
}

export const TopLanguagesCard: React.FC<TopLanguagesCardProps> = ({ 
  languages, 
  loading, 
  error 
}) => {
  // Get top 3 languages by total_code_lines_suggested
  const topLanguages = languages.slice(0, 3);

  // Language icon mapping
  const getLanguageIcon = (language: string): string => {
    const iconMap: Record<string, string> = {
      javascript: '🟨',
      typescript: '🔵',
      python: '🐍',
      java: '☕',
      csharp: '🟢',
      cpp: '🔷',
      ruby: '🔴',
      go: '🔹',
      rust: '🦀',
      php: '🐘',
      swift: '🦅',
      kotlin: '🟣',
      scala: '🔺',
      html: '🟠',
      css: '🎨',
      sql: '🗄️',
      shell: '🐚',
      powershell: '💙',
      yaml: '📄',
      json: '📋',
      markdown: '📝',
      dockerfile: '🐳',
      // Add more as needed
    };

    return iconMap[language.toLowerCase()] || '📜';
  };

  // Get color based on acceptance rate
  const getAcceptanceRateColor = (rate: number): string => {
    if (rate >= 0.7) return 'text-green-600';
    if (rate >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center h-48">
          <p className="text-gray-500">Loading language data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center h-48">
          <p className="text-red-500">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (topLanguages.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center h-48">
          <p className="text-gray-500">No language data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {topLanguages.map((lang, index) => (
        <div key={lang.language} className="bg-white rounded-lg shadow-md p-6 flex flex-col">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-2xl bg-indigo-50 rounded-full">
              {getLanguageIcon(lang.language)}
            </div>
            <div className="ml-3">
              <h3 className="font-semibold text-lg capitalize">{lang.language}</h3>
              <p className="text-sm text-gray-500">
                {index === 0 ? '1er' : index === 1 ? '2ème' : '3ème'} plus utilisé
              </p>
            </div>
          </div>
          
          <div className="space-y-3 flex-grow">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Lignes suggérées</span>
                <span className="font-medium text-black">{lang.total_code_lines_suggested.toLocaleString()}</span>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Lignes acceptées</span>
                <span className="font-medium text-black">{lang.total_code_lines_accepted.toLocaleString()}</span>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Taux d&apos;acceptation</span>
                <span className={`font-medium text-black ${getAcceptanceRateColor(lang.completion_acceptance_rate)}`}>
                  {(lang.completion_acceptance_rate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="h-2.5 rounded-full" 
                  style={{ 
                    width: `${Math.min(lang.completion_acceptance_rate * 100, 100)}%`,
                    backgroundColor: index === 0 ? '#4F46E5' : index === 1 ? '#6366F1' : '#818CF8'
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}; 