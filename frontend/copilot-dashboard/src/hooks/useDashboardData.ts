import { useState, useEffect } from 'react';
import { TransformedBillingRecord } from '@/types/billing';
import { DashboardData } from '@/types/dashboard';

export const useDashboardData = (startDate: Date, endDate: Date) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  // Load and process CSV data
  const loadData = async (startDate: Date, endDate: Date): Promise<DashboardData | null> => {
    try {
      const response = await fetch('/api/metrics');
      const csvData: TransformedBillingRecord[] = await response.json();
      
      // Filter data based on date range
      const filteredData = csvData.filter(row => {
        const date = new Date(row.extract_date);
        return date >= startDate && date <= endDate;
      });
      
      // Process the data
      const dates = filteredData.map((row) => new Date(row.extract_date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }));
      const activeUsers = filteredData.map((row) => row.total);
      const engagedUsers = filteredData.map((row) => row.total_engaged_users);
      
      // Calculate metrics
      const latestActiveUsers = engagedUsers[engagedUsers.length - 1] || 0;
      const totalDevs = Math.max(...activeUsers, 0);
      const hoursSaved = engagedUsers.reduce((sum: number, users: number) => sum + users * 0.7, 0);
      const costSavings = hoursSaved * 107; // Assuming $50 per hour saved

      return {
        activeUsers: latestActiveUsers,
        totalDevs,
        hoursSaved,
        costSavings,
        timeSeriesData: {
          labels: dates,
          datasets: [
            {
              label: 'Heures potentielles économisées',
              data: activeUsers.map(users => users * 0.5),
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.1)',
              type: 'line' as const,
              yAxisID: 'y'
            },
            {
              label: 'Heures économisées',
              data: engagedUsers.map(users => users * 0.5),
              backgroundColor: 'rgba(0, 182, 255, 0.5)',
              borderColor: 'rgb(0, 182, 255)',
              type: 'bar' as const,
              yAxisID: 'y'
            }
          ]
        },
        costSavingsData: {
          labels: dates,
          datasets: [{
            label: 'Économies quotidiennes ($)',
            data: engagedUsers.map(users => users * 50 * 0.7),
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgb(75, 192, 192)',
            type: 'bar' as const
          },
          {
            label: 'Économies quotidiennes potentielles  ($)',
            data: activeUsers.map(users => users * 50 * 0.7),
            backgroundColor: 'rgba(173, 24, 31, 0.5)',
            borderColor: 'rgb(172, 43, 43)',
            type: 'line' as const
          }]
        }
      };
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      return null;
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const result = await loadData(startDate, endDate);
      setData(result);
      setLoading(false);
    };
    fetchData();
  }, [startDate, endDate]);

  return { data, loading };
};