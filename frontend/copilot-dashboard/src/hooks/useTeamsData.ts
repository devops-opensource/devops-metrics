import { useState, useEffect } from 'react';
import { TeamMetricsData } from '@/types/teams';

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

export function useTeamsData(startDate: Date, endDate: Date, selectedTeam: string) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

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

  return { data, loading };
}

export type { DashboardData };