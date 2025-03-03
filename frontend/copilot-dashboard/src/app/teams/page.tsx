'use client';

import { useState, useEffect } from 'react';
import { MetricCard } from '../../components/MetricCard';
import { TimeSeriesChart } from '../../components/TimeSeriesChart';
import { TopLanguagesCard } from '../../components/TopLanguagesCard';
import { DateRangePicker } from '../../components/DateRangePicker';
import Select from 'react-select';
import { useTeamsData } from '@/hooks/useTeamsData';
import { useLanguageData } from '@/hooks/useLanguageData';

interface ChatMetric {
  team: string;
  // Add other fields if needed
}

export default function Teams() {
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  });
  const [endDate, setEndDate] = useState(() => new Date());

  const { data, loading } = useTeamsData(startDate, endDate, selectedTeam);
  const { data: languageData, loading: languageLoading, error: languageError } = useLanguageData(selectedTeam);

  useEffect(() => {
    const initializeTeams = async () => {
      const result = await fetch('/api/metrics/chat').then(res => res.json()) as ChatMetric[];
      const teams = [...new Set(result.map((row: ChatMetric) => row.team))];
      if (teams.length) {
        setSelectedTeam(teams[0]);
      }
    };
    initializeTeams();
  }, []);

  if (loading || !data) {
    return <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
      <div className="text-xl">Chargement des données...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Métriques d&apos;efficacité de l&apos;équipe</h1>
            <p className="text-gray-600">
              Analysez la performance de l&apos;équipe avec GitHub Copilot
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500 mb-1">Dernière mise à jour</p>
            <p className="font-medium">{new Date().toLocaleDateString('fr-FR', { 
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            })}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-6">
          <div className="w-64 h-full">
            <Select
              options={data.teams.map(team => ({ value: team, label: team }))}
              value={{ value: selectedTeam, label: selectedTeam }}
              onChange={(option) => option && setSelectedTeam(option.value)}
              className="text-sm"
              placeholder="Sélectionnez une équipe..."
              styles={{
                control: (base) => ({
                  ...base,
                  backgroundColor: 'white',
                  height: '40px', // Fixed height to match DateRangePicker
                }),
                option: (base) => ({
                  ...base,
                  color: '#1f2937',
                }),
                singleValue: (base) => ({
                  ...base,
                  color: '#1f2937',
                }),
                placeholder: (base) => ({
                  ...base,
                  color: '#6b7280',
                }),
              }}
            />
          </div>
          <div className="h-full">
            <DateRangePicker
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Taux moyen de complétion"
            value={data.metrics.avgCompletionRate * 100}
            description="Taux moyen d&apos;acceptation de la complétion de code"
            globalValue={data.metrics.avgGlobalCompletionRate * 100}
            unit="%"
          />
          <MetricCard
            title="Taux moyen d&apos;acceptation du chat"
            value={data.metrics.avgChatAcceptanceRate * 100}
            description="Taux moyen d&apos;acceptation des suggestions de chat"
            globalValue={data.metrics.avgGlobalChatAcceptanceRate * 100}
            unit="%"
          />
          <MetricCard
            title="Chats moyens par utilisateur"
            value={data.metrics.avgChatPerUser}
            description="Nombre moyen d'interactions de chat par utilisateur"
            unit=""
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div>
            <TimeSeriesChart
              title="Taux d'acceptation de la complétion"
              data={data.timeSeriesData}
              height={300}
            />
          </div>
          <div>
            <TimeSeriesChart
              title="Taux d'acceptation du chat"
              data={data.chatAcceptanceData}
              height={300}
            />
          </div>
          <div>
            <TimeSeriesChart
              title="Chats par utilisateur"
              data={data.chatPerUserData}
              height={300}
            />
          </div>
        </div>

        {/* Top Languages Section */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Langages les plus utilisés</h2>
            <p className="text-gray-600 mb-6">
              Les trois langages de programmation avec le plus grand nombre de lignes de code suggérées pour l&apos;équipe sélectionnée,
              ainsi que leur taux d&apos;acceptation de complétion.
            </p>
            
            {languageLoading ? (
              <div className="flex items-center justify-center h-48">
                <p className="text-gray-500">Chargement des données de langage...</p>
              </div>
            ) : languageError ? (
              <div className="flex items-center justify-center h-48">
                <p className="text-red-500">Erreur: {languageError}</p>
              </div>
            ) : (
              <TopLanguagesCard 
                languages={languageData} 
                loading={false} 
                error={null} 
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 