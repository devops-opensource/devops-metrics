'use client';

import { useState, useEffect } from 'react';
import { MetricCard } from '../components/MetricCard';
import { TimeSeriesChart } from '../components/TimeSeriesChart';
import { Settings } from '../components/Settings';
import { DateRangePicker } from '../components/DateRangePicker';

interface MetricsData {
  date: string;
  total_active_users: string;
  total_engaged_users: string;
}

interface DashboardData {
  activeUsers: number;
  totalDevs: number;
  hoursSaved: number;
  costSavings: number;
  timeSeriesData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor: string;
      type: 'line' | 'bar';
      yAxisID?: string;
    }[];
  };
  costSavingsData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor: string;
      borderColor: string;
      type: 'line' | 'bar';
    }[];
  };
}

// Load and process CSV data
const loadData = async (startDate: Date, endDate: Date): Promise<DashboardData | null> => {
  try {
    const response = await fetch('/api/metrics');
    const csvData: MetricsData[] = await response.json();
    
    // Filter data based on date range
    const filteredData = csvData.filter(row => {
      const date = new Date(row.date);
      return date >= startDate && date <= endDate;
    });
    
    // Process the data
    const dates = filteredData.map((row) => new Date(row.date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }));
    const activeUsers = filteredData.map((row) => parseInt(row.total_active_users));
    const engagedUsers = filteredData.map((row) => parseInt(row.total_engaged_users));
    
    // Calculate metrics
    const latestActiveUsers = activeUsers[activeUsers.length - 1] || 0;
    const totalDevs = Math.max(...activeUsers, 0);
    const hoursSaved = engagedUsers.reduce((sum: number, users: number) => sum + users * 8, 0); // Assuming 8 hours per day
    const costSavings = hoursSaved * 50; // Assuming $50 per hour saved

    return {
      activeUsers: latestActiveUsers,
      totalDevs,
      hoursSaved,
      costSavings,
      timeSeriesData: {
        labels: dates,
        datasets: [
          {
            label: 'Active Users',
            data: activeUsers,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            type: 'line' as const,
            yAxisID: 'y1'
          },
          {
            label: 'Hours Saved',
            data: engagedUsers.map(users => users * 8),
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
          label: 'Daily Savings ($)',
          data: engagedUsers.map(users => users * 50 * 8), // $50 per hour, 8 hours per day
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgb(75, 192, 192)',
          type: 'bar' as const
        }]
      }
    };
  } catch (error) {
    console.error('Error loading data:', error);
    return null;
  }
};

export default function Home() {
  const [maxDevs, setMaxDevs] = useState(200);
  const [meanSalary, setMeanSalary] = useState(100000);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  });
  const [endDate, setEndDate] = useState(() => new Date());

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const result = await loadData(startDate, endDate);
      setData(result);
      setLoading(false);
    };
    fetchData();
  }, [startDate, endDate]);

  if (loading || !data) {
    return <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
      <div className="text-xl">Chargement des données...</div>
    </div>;
  }

  const potentialAnnualSavings = maxDevs * 50 * 48 * 3.5;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Gologic</h1>
            <p className="text-gray-600">
              Potential Annual Savings: {maxDevs} devs X $50/hr X 48 weeks X 3.5/hrs = ${(potentialAnnualSavings / 1000000).toFixed(2)}M
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

        <div className="mb-6">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Hours Saved"
            value={data.hoursSaved}
            description="Estimated number of hours saved by using GitHub Copilot"
          />
          <MetricCard
            title="Cost Savings"
            value={`$${data.costSavings.toLocaleString()}`}
            description="Estimated value in dollars based on salary and time saved"
          />
          <MetricCard
            title="Total Devs"
            value={data.totalDevs}
            description="Number of developers within the organization"
          />
          <MetricCard
            title="Avg Active Devs"
            value={data.activeUsers}
            description="Average number of active developers"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <TimeSeriesChart
              title="Engagement and Hours Saved"
              data={data.timeSeriesData}
              height={400}
            />
          </div>
          <div>
            <Settings
              maxDevs={maxDevs}
              meanSalary={meanSalary}
              onMaxDevsChange={setMaxDevs}
              onMeanSalaryChange={setMeanSalary}
            />
          </div>
        </div>

        <div className="mb-8">
          <TimeSeriesChart
            title="Daily Cost Savings"
            data={data.costSavingsData}
            height={300}
          />
        </div>
      </div>
    </div>
  );
}
