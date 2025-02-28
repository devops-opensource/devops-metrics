import type { TimeSeriesData } from '../components/TimeSeriesChart';

export interface DashboardData {
  activeUsers: number;
  totalDevs: number;
  hoursSaved: number;
  costSavings: number;
  timeSeriesData: TimeSeriesData;
  costSavingsData: TimeSeriesData;
}