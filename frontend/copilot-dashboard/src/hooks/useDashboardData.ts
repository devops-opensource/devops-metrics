import { useState, useEffect } from 'react';
import { TransformedBillingRecord } from '@/types/billing';
import { DashboardData } from '@/types/dashboard';
import { useMetricsStore } from '@/store/metricsStore';

const isWeekend = (date: Date): boolean => {
  const day = date.getDay();
  return day === 6 || day === 0; 
};

const filterDataByDateRange = (data: TransformedBillingRecord[], startDate: Date, endDate: Date) => {
  return data.filter(row => {
    const date = new Date(row.extract_date);
    return date >= startDate && date <= endDate && !isWeekend(date);
  });
};

const formatDates = (data: TransformedBillingRecord[]) => {
  return data.map((row) => {
    const date = new Date(row.extract_date);
    // Set the time to noon UTC to avoid timezone issues
    date.setUTCHours(12, 0, 0, 0);
    return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric', timeZone: 'UTC' });
  });
};

const calculateMetrics = (filteredData: TransformedBillingRecord[]) => {
  const totalUsers = filteredData.map((row) => row.total);
  const activeUsers = filteredData.map((row) => row.total_active_users);
  const engagedUsers = filteredData.map((row) => row.total_engaged_users);
  
  return {
    latestActiveUsers: activeUsers.reduce((sum, users) => sum + users, 0) / activeUsers.length || 0,
    totalDevs:  totalUsers[totalUsers.length - 1] || 0,
    hoursSaved: activeUsers.reduce((sum: number, users: number) => sum + users * 0.7, 0),
    activeUsers,
    engagedUsers
  };
};

const createTimeSeriesData = (dates: string[], activeUsers: number[], totalUsers: number) => {
  return {
    labels: dates,
    datasets: [
      {
        label: 'Heures potentielles économisées',
        data: Array(dates.length).fill(totalUsers * 0.7),
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderColor: 'rgb(255, 99, 132)',
        type: 'line' as const,
        yAxisID: 'y'
      },
      {
        label: 'Heures économisées', 
        data: activeUsers.map(users => users * 0.7),
        backgroundColor: 'rgba(0, 182, 255, 0.5)',
        borderColor: 'rgb(0, 182, 255)',
        type: 'bar' as const,
        yAxisID: 'y'
      }

    ]
  };
};

const createCostSavingsData = (dates: string[], activeUsers: number[], totalUsers: number, hourlyRate: number) => {
  return {
    labels: dates,
    datasets: [{
      label: 'Économies quotidiennes ($)',
      data: activeUsers.map(users => users * hourlyRate * 0.7),
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      borderColor: 'rgb(75, 192, 192)',
      type: 'bar' as const
    },
    {
      label: 'Économies quotidiennes potentielles  ($)',
      data: Array(dates.length).fill(totalUsers * hourlyRate * 0.7),
      backgroundColor: 'rgba(173, 24, 31, 0.5)',
      borderColor: 'rgb(172, 43, 43)',
      type: 'line' as const
    }]
  };
};

const createUsersActivityData = (dates: string[], activeUsers: number[], engagedUsers: number[]) => {
  return {
    labels: dates,
    datasets: [
      {
        label: 'Développeurs actifs',
        data: activeUsers,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgb(54, 162, 235)',
        type: 'bar' as const
      },
      {
        label: 'Développeurs engagés',
        data: engagedUsers,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgb(75, 192, 192)',
        type: 'bar' as const
      }
    ]
  };
};

const loadData = async (startDate: Date, endDate: Date, hourlyRate: number): Promise<DashboardData | null> => {
  try {
    const response = await fetch('/api/metrics');
    const csvData: TransformedBillingRecord[] = await response.json();
    
    const filteredData = filterDataByDateRange(csvData, startDate, endDate);
    const dates = formatDates(filteredData);
    const metrics = calculateMetrics(filteredData);
    
    return {
      activeUsers: metrics.latestActiveUsers,
      totalDevs: metrics.totalDevs,
      hoursSaved: metrics.hoursSaved,
      costSavings: metrics.hoursSaved * hourlyRate,
      timeSeriesData: createTimeSeriesData(dates, metrics.activeUsers, metrics.totalDevs),
      costSavingsData: createCostSavingsData(dates, metrics.activeUsers, metrics.totalDevs, hourlyRate),
      usersActivityData: createUsersActivityData(dates, metrics.activeUsers, metrics.engagedUsers)
    };
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
    return null;
  }
};

export const useDashboardData = (startDate: Date, endDate: Date) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const { hourlyRate } = useMetricsStore();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const result = await loadData(startDate, endDate, hourlyRate);
      setData(result);
      setLoading(false);
    };
    fetchData();
  }, [startDate, endDate, hourlyRate]);

  return { data, loading };
};