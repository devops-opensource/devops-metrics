import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Scale,
  CoreScaleOptions,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TimeSeriesChartProps {
  title: string;
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor?: string;
      type: 'line' | 'bar';
      yAxisID?: string;
    }[];
  };
  height?: number;
  showGrid?: boolean;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ 
  title, 
  data, 
  height = 300,
  showGrid = true 
}) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        }
      },
      title: {
        display: true,
        text: title,
        padding: {
          top: 10,
          bottom: 20
        },
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        titleColor: '#000',
        bodyColor: '#666',
        borderColor: '#ddd',
        borderWidth: 1,
        padding: 10,
        boxPadding: 5,
        usePointStyle: true,
      }
    },
    scales: {
      x: {
        type: 'category' as const,
        grid: {
          display: showGrid,
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 10
        }
      },
      y: {
        type: 'linear' as const,
        beginAtZero: true,
        grid: {
          display: showGrid,
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function(this: Scale<CoreScaleOptions>, tickValue: number | string) {
            const value = Number(tickValue);
            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
            return value;
          }
        }
      },
      y1: {
        type: 'linear' as const,
        beginAtZero: true,
        position: 'right' as const,
        grid: {
          display: false,
        },
        ticks: {
          callback: function(this: Scale<CoreScaleOptions>, tickValue: number | string) {
            const value = Number(tickValue);
            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
            return value;
          }
        }
      }
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md" style={{ height }}>
      <Chart type='bar' options={options} data={data} />
    </div>
  );
}; 