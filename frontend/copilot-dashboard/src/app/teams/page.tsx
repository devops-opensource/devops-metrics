'use client';

import { useState, useEffect } from 'react';
import { MetricCard } from '../../components/MetricCard';
import { TimeSeriesChart } from '../../components/TimeSeriesChart';
import { DateRangePicker } from '../../components/DateRangePicker';
import Select from 'react-select';

interface TeamMetricsData {
  team: string;
  date: string;
  completion_acceptance_rate: number;
  chat_acceptance_rate: number;
  chat_per_user: number;
  total_chat: string;
  total_engaged_users: string;
}

interface DashboardData {
  teams: string[];
  selectedTeam: string;
  metrics: {
    avgCompletionRate: number;
    avgChatAcceptanceRate: number;
    avgChatPerUser: number;
    avgGlobalCompletionRate: number;
    avgGlobalChatAcceptanceRate: number;
  };
  timeSeriesData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor: string;
      type: 'line';
      yAxisID?: string;
      borderDash?: number[];
    }[];
  };
  chatAcceptanceData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor: string;
      type: 'line';
      yAxisID?: string;
      borderDash?: number[];
    }[];
  };
  chatPerUserData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor: string;
      type: 'line';
      yAxisID?: string;
      borderDash?: number[];
    }[];
  };
}

// Reduce cognitive load by splitting the code into smaller functions
// Load and process CSV data
const loadData = async (startDate: Date, endDate: Date, selectedTeam: string): Promise<DashboardData | null> => {
  try {
    const [chatResponse, completionResponse, chatGlobalResponse, completionGlobalResponse] = await Promise.all([
      fetch('/api/metrics/chat'),
      fetch('/api/metrics/completion'),
      fetch('/api/metrics/chat/global'),
      fetch('/api/metrics/completion/global')
    ]);

    const chatData: TeamMetricsData[] = await chatResponse.json();
    const completionData: TeamMetricsData[] = await completionResponse.json();
    const chatGlobalData: TeamMetricsData[] = await chatGlobalResponse.json();
    const completionGlobalData: TeamMetricsData[] = await completionGlobalResponse.json();
    
    // Get unique teams
    const teams = [...new Set(chatData.map((row: TeamMetricsData) => row.team))];
    
    // Filter data based on date range and team
    const filteredChatData = chatData.filter((row: TeamMetricsData) => {
      const date = new Date(row.date);
      return date >= startDate && date <= endDate && row.team === selectedTeam;
    });

    const filteredCompletionData = completionData.filter((row: TeamMetricsData) => {
      const date = new Date(row.date);
      return date >= startDate && date <= endDate && row.team === selectedTeam;
    });

    const filteredChatGlobalData = chatGlobalData.filter((row: TeamMetricsData) => {
      const date = new Date(row.date);
      return date >= startDate && date <= endDate;
    });

    const filteredCompletionGlobalData = completionGlobalData.filter((row: TeamMetricsData) => {
      const date = new Date(row.date);
      return date >= startDate && date <= endDate;
    });
    
    // Process the data
    const dates = filteredChatData.map((row: TeamMetricsData) => 
      new Date(row.date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' })
    );

    // Calculate averages
    const avgCompletionRate = filteredCompletionData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (row.completion_acceptance_rate || 0), 0) / filteredCompletionData.length || 0;

    const avgChatAcceptanceRate = filteredChatData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (row.chat_acceptance_rate || 0), 0) / filteredChatData.length || 0;

    // Calculate total chats and total users for the period
    const totalChats = filteredChatData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (parseInt(row.total_chat) || 0), 0);
    const totalUsers = filteredChatData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (parseInt(row.total_engaged_users) || 0), 0);
    const avgChatPerUser = totalUsers > 0 ? totalChats / totalUsers : 0;

    // Calculate global averages
    const avgGlobalCompletionRate = filteredCompletionGlobalData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (row.completion_acceptance_rate || 0), 0) / filteredCompletionGlobalData.length || 0;

    const avgGlobalChatAcceptanceRate = filteredChatGlobalData.reduce((sum: number, row: TeamMetricsData) => 
      sum + (row.chat_acceptance_rate || 0), 0) / filteredChatGlobalData.length || 0;

    return {
      teams,
      selectedTeam,
      metrics: {
        avgCompletionRate,
        avgChatAcceptanceRate,
        avgChatPerUser,
        avgGlobalCompletionRate,
        avgGlobalChatAcceptanceRate
      },
      timeSeriesData: {
        labels: dates,
        datasets: [
          {
            label: selectedTeam,
            data: filteredCompletionData.map((row: TeamMetricsData) => row.completion_acceptance_rate * 100),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            type: 'line'
          },
          {
            label: 'Organization',
            data: filteredCompletionGlobalData.map((row: TeamMetricsData) => row.completion_acceptance_rate * 100),
            borderColor: 'rgb(128, 128, 128)',
            backgroundColor: 'rgba(128, 128, 128, 0.1)',
            type: 'line',
            borderDash: [5, 5]
          }
        ]
      },
      chatAcceptanceData: {
        labels: dates,
        datasets: [
          {
            label: selectedTeam,
            data: filteredChatData.map((row: TeamMetricsData) => row.chat_acceptance_rate * 100),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            type: 'line'
          },
          {
            label: 'Organization',
            data: filteredChatGlobalData.map((row: TeamMetricsData) => row.chat_acceptance_rate * 100),
            borderColor: 'rgb(128, 128, 128)',
            backgroundColor: 'rgba(128, 128, 128, 0.1)',
            type: 'line',
            borderDash: [5, 5]
          }
        ]
      },
      chatPerUserData: {
        labels: dates,
        datasets: [
          {
            label: selectedTeam,
            data: filteredChatData.map((row: TeamMetricsData) => row.chat_per_user),
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            type: 'line'
          },
          {
            label: 'Organization',
            data: filteredChatGlobalData.map((row: TeamMetricsData) => row.chat_per_user),
            borderColor: 'rgb(128, 128, 128)',
            backgroundColor: 'rgba(128, 128, 128, 0.1)',
            type: 'line',
            borderDash: [5, 5]
          }
        ]
      }
    };
  } catch (error) {
    console.error('Error loading data:', error);
    return null;
  }
};

export default function Teams() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  });
  const [endDate, setEndDate] = useState(() => new Date());

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedTeam) return;
      setLoading(true);
      const result = await loadData(startDate, endDate, selectedTeam);
      setData(result);
      setLoading(false);
    };
    fetchData();
  }, [startDate, endDate, selectedTeam]);

  useEffect(() => {
    const initializeTeams = async () => {
      const result = await loadData(startDate, endDate, 'equipe-github');
      if (result?.teams.length) {
        setSelectedTeam(result.teams[0]);
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
            <h1 className="text-3xl font-bold mb-2">Team Efficiency Metrics</h1>
            <p className="text-gray-600">
              Analyze team performance with GitHub Copilot
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500 mb-1">Last Refresh</p>
            <p className="font-medium">{new Date().toLocaleDateString('en-US', { 
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
              placeholder="Select a team..."
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
            title="Avg Completion Rate"
            value={data.metrics.avgCompletionRate * 100}
            description="Average code completion acceptance rate"
            globalValue={data.metrics.avgGlobalCompletionRate * 100}
            unit="%"
          />
          <MetricCard
            title="Avg Chat Acceptance"
            value={data.metrics.avgChatAcceptanceRate * 100}
            description="Average chat suggestions acceptance rate"
            globalValue={data.metrics.avgGlobalChatAcceptanceRate * 100}
            unit="%"
          />
          <MetricCard
            title="Avg Chat Per User"
            value={data.metrics.avgChatPerUser}
            description="Average number of chat interactions per user"
            unit=""
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div>
            <TimeSeriesChart
              title="Completion Acceptance Rate"
              data={data.timeSeriesData}
              height={300}
            />
          </div>
          <div>
            <TimeSeriesChart
              title="Chat Acceptance Rate"
              data={data.chatAcceptanceData}
              height={300}
            />
          </div>
          <div>
            <TimeSeriesChart
              title="Chat Per User"
              data={data.chatPerUserData}
              height={300}
            />
          </div>
        </div>
      </div>
    </div>
  );
} 