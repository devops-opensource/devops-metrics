import React from 'react';
import type { FC } from 'react';
import type { DashboardData } from '@/types/dashboard';
import { MetricCard } from './MetricCard';

export interface DashboardMetricsProps {
  data: DashboardData;
}

export const DashboardMetrics: FC<DashboardMetricsProps> = ({ data }) => {
  // Convertir les économies en millions de dollars avec 2 décimales
  const costSavingsInMillions = (data.costSavings / 1000000).toFixed(2);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
{/*       <MetricCard
        title="Heures économisées"
        value={data.hoursSaved}
        description="Nombre estimé d'heures économisées grâce à GitHub Copilot sur la période sélectionnée"
        unit="h"
      /> */}
      <MetricCard
        title="Économies confirmées"
        value={costSavingsInMillions}
        description="Valeur estimée en millions de dollars basée sur le salaire et le temps économisé sur la période sélectionnée"
        unit="M$"
      />
      <MetricCard
        title="Total développeurs"
        value={data.totalDevs}
        description="Nombre de développeurs dans l'organisation avec une licence"
        unit="devs"
      />
      <MetricCard
        title="Moy. développeurs actifs"
        value={data.activeUsers}
        description="Nombre moyen de développeurs actifs"
        unit="devs"
      />
    </div>
  );
};