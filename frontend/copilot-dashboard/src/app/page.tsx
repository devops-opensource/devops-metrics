'use client';

import { useState } from 'react';
import type { ReactElement } from 'react';
import { TimeSeriesChart } from '../components/TimeSeriesChart';
import { DateRangePicker } from '../components/DateRangePicker';
import { DashboardHeader } from '../components/DashboardHeader';
import { DashboardMetrics } from '../components/DashboardMetrics';
import { useDashboardData } from '@/hooks/useDashboardData';

export default function Home(): ReactElement {
  const [startDate, setStartDate] = useState<Date>(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  });
  const [endDate, setEndDate] = useState<Date>(() => new Date());

  const { data, loading } = useDashboardData(startDate, endDate);

  if (loading || !data) {
    return <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
      <div className="text-xl">Chargement des données...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader />

        <div className="mb-6">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
        </div>

        <DashboardMetrics data={data} />

{/*         <div className="mb-8">
          <TimeSeriesChart
            title="Engagement et heures économisées"
            data={data.timeSeriesData}
            height={400}
          />
        </div> */}

        <div className="mb-8">
          <TimeSeriesChart
            title="Économies quotidiennes"
            data={data.costSavingsData}
            height={300}
          />
        </div>

        <div className="mb-8">
          <TimeSeriesChart
            title="Activité des développeurs"
            data={data.usersActivityData}
            height={300}
          />
        </div>


      </div>
    </div>
  );
}
