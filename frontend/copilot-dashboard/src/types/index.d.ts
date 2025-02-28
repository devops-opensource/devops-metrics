import { DashboardData } from './dashboard';

declare module '@/hooks/useDashboardData' {
  export function useDashboardData(startDate: Date, endDate: Date): {
    data: DashboardData | null;
    loading: boolean;
  };
}