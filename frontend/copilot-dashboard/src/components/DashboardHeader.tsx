import React, { useState, useEffect } from 'react';
import type { FC } from 'react';
import { useMetricsStore } from '@/store/metricsStore';
import { useDebounce } from '@/hooks/useDebounce';

export interface DashboardHeaderProps {
  initialTitle?: string;
}

export const DashboardHeader: FC<DashboardHeaderProps> = ({ 
  initialTitle = "Gologic"
}) => {
  const [showFormulaDetails, setShowFormulaDetails] = useState(false);
  const [title, setTitle] = useState(initialTitle);
  const [localHourlyRate, setLocalHourlyRate] = useState("");

  const { 
    maxDevs, 
    hourlyRate, 
    weeksPerYear, 
    hoursPerWeek,
    setMaxDevs,
    setHourlyRate,
    setWeeksPerYear,
    setHoursPerWeek
  } = useMetricsStore();

  const debouncedHourlyRate = useDebounce(localHourlyRate, 500);

  // Initialize local hourly rate and handle updates from store
  useEffect(() => {
    if (hourlyRate.toString() !== localHourlyRate) {
      setLocalHourlyRate(hourlyRate.toString());
    }
  }, [hourlyRate]);

  // Update global store when debounced value changes
  useEffect(() => {
    if (debouncedHourlyRate && debouncedHourlyRate !== hourlyRate.toString()) {
      setHourlyRate(Number(debouncedHourlyRate));
    }
  }, [debouncedHourlyRate, setHourlyRate, hourlyRate]);

  const potentialAnnualSavings = maxDevs * hourlyRate * weeksPerYear * hoursPerWeek;
  const formattedSavings = (potentialAnnualSavings / 1000000).toFixed(2);

  const handleToggleDetails = () => {
    setShowFormulaDetails(prev => !prev);
  };

  const handleMaxDevsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMaxDevs(Number(e.target.value));
  };

  const handleHourlyRateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalHourlyRate(e.target.value);
  };

  const handleWeeksPerYearChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWeeksPerYear(Number(e.target.value));
  };

  const handleHoursPerWeekChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHoursPerWeek(Number(e.target.value));
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <input
            type="text"
            value={title}
            onChange={handleTitleChange}
            className="text-3xl font-bold mb-2 text-indigo-700 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 rounded px-1"
            aria-label="Company name"
          />
          <div className="flex items-center">
            <p className="text-gray-700 font-medium">
              Économies annuelles potentielles: <span className="text-indigo-600 font-bold text-xl">{formattedSavings}M$</span>
            </p>
            <button 
              onClick={handleToggleDetails}
              className="ml-2 text-indigo-500 hover:text-indigo-700 focus:outline-none"
              aria-label={showFormulaDetails ? "Masquer les détails" : "Afficher les détails"}
              tabIndex={0}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                {showFormulaDetails ? (
                  <path fillRule="evenodd" d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clipRule="evenodd" />
                ) : (
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                )}
              </svg>
            </button>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500 mb-1">Dernière mise à jour</p>
          <p className="font-medium text-gray-700">{new Date().toLocaleDateString('fr-FR', { 
            month: 'long',
            day: 'numeric',
            year: 'numeric'
          })}</p>
        </div>
      </div>

      {showFormulaDetails && (
        <div className="bg-indigo-50 p-4 rounded-lg mb-4 animate-fadeIn">
          <p className="text-gray-700 mb-4">Ajustez les paramètres pour calculer les économies potentielles:</p>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label htmlFor="maxDevs" className="block text-sm font-medium text-gray-700 mb-1">
                Nombre de développeurs
              </label>
              <div className="relative rounded-md shadow-sm">
                <input
                  type="number"
                  id="maxDevs"
                  className="block w-full rounded-md border-gray-300 pl-3 pr-12 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  value={maxDevs}
                  onChange={handleMaxDevsChange}
                  min="1"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <span className="text-gray-500 sm:text-sm">devs</span>
                </div>
              </div>
            </div>
            <div>
              <label htmlFor="hourlyRate" className="block text-sm font-medium text-gray-700 mb-1">
                Taux horaire
              </label>
              <div className="relative rounded-md shadow-sm">
                <input
                  type="number"
                  id="hourlyRate"
                  className="block w-full rounded-md border-gray-300 pl-3 pr-12 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  value={localHourlyRate}
                  onChange={handleHourlyRateChange}
                  min="1"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <span className="text-gray-500 sm:text-sm">$/h</span>
                </div>
              </div>
            </div>
            <div>
              <label htmlFor="weeksPerYear" className="block text-sm font-medium text-gray-700 mb-1">
                Semaines par année
              </label>
              <div className="relative rounded-md shadow-sm">
                <input
                  type="number"
                  id="weeksPerYear"
                  className="block w-full rounded-md border-gray-300 pl-3 pr-12 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  value={weeksPerYear}
                  onChange={handleWeeksPerYearChange}
                  min="1"
                  max="52"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <span className="text-gray-500 sm:text-sm">sem</span>
                </div>
              </div>
            </div>
            <div>
              <label htmlFor="hoursPerWeek" className="block text-sm font-medium text-gray-700 mb-1">
                Heures par semaine
              </label>
              <div className="relative rounded-md shadow-sm">
                <input
                  type="number"
                  id="hoursPerWeek"
                  className="block w-full rounded-md border-gray-300 pl-3 pr-12 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  value={hoursPerWeek}
                  onChange={handleHoursPerWeekChange}
                  min="0.1"
                  step="0.1"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <span className="text-gray-500 sm:text-sm">h</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-white rounded-md shadow-sm">
            <p className="text-gray-700 font-medium">
              Formule: {maxDevs} devs × {hourlyRate}$/h × {weeksPerYear} semaines × {hoursPerWeek}h = {formattedSavings}M$
            </p>
          </div>
        </div>
      )}
    </div>
  );
};