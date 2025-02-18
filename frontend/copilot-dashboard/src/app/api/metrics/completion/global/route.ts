import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

interface CompletionGlobalRecord {
  date: string;
  language: string;
  total_code_lines_accepted: string;
  total_code_lines_suggested: string;
  completion_acceptance_rate: string;
}

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', '..', 'notebooks', 'copilot_metrics_completion_global.csv');
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    }) as CompletionGlobalRecord[];

    // Group by date and calculate average completion rate
    const groupedData = records.reduce((acc: { [key: string]: { total: number; count: number } }, record) => {
      const { date, completion_acceptance_rate } = record;
      if (!acc[date]) {
        acc[date] = { total: 0, count: 0 };
      }
      acc[date].total += parseFloat(completion_acceptance_rate);
      acc[date].count += 1;
      return acc;
    }, {});

    // Transform to match TeamMetricsData interface
    const transformedRecords = Object.entries(groupedData).map(([date, data]) => ({
      team: 'Global',
      date,
      completion_acceptance_rate: data.total / data.count,
      chat_acceptance_rate: 0, // Will be populated from chat data
      chat_per_user: 0 // Will be populated from chat data
    }));

    return NextResponse.json(transformedRecords);
  } catch (error) {
    console.error('Error reading global completion metrics:', error);
    return NextResponse.json({ error: 'Failed to load global completion metrics' }, { status: 500 });
  }
} 