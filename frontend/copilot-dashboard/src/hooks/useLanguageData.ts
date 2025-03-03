import { useState, useEffect } from 'react';

interface LanguageData {
  language: string;
  total_code_lines_suggested: number;
  total_code_lines_accepted: number;
  completion_acceptance_rate: number;
}

export function useLanguageData(selectedTeam: string) {
  const [data, setData] = useState<LanguageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedTeam) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/metrics/completion/languages?team=${encodeURIComponent(selectedTeam)}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch language data: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        console.error('Error fetching language data:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedTeam]);

  return { data, loading, error };
}

export type { LanguageData }; 