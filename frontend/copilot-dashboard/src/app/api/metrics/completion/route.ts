import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

interface CompletionRecord {
  team: string;
  date: string;
  total_code_lines_accepted: string;
  total_code_lines_suggested: string;
}

interface AggregatedRecord {
  team: string;
  date: string;
  total_lines_accepted: number;
  total_lines_suggested: number;
  completion_acceptance_rate: number;
}

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', '..', 'notebooks', 'copilot_metrics_completion_team.csv');
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    }) as CompletionRecord[];

    // Group by team and date to calculate average completion rate
    const aggregatedData = records.reduce((acc: AggregatedRecord[], record: CompletionRecord) => {
      const key = `${record.team}-${record.date}`;
      const existingRecord = acc.find(r => `${r.team}-${r.date}` === key);

      if (existingRecord) {
        existingRecord.total_lines_accepted += parseInt(record.total_code_lines_accepted);
        existingRecord.total_lines_suggested += parseInt(record.total_code_lines_suggested);
        existingRecord.completion_acceptance_rate = 
          existingRecord.total_lines_accepted / existingRecord.total_lines_suggested;
      } else {
        acc.push({
          team: record.team,
          date: record.date,
          total_lines_accepted: parseInt(record.total_code_lines_accepted),
          total_lines_suggested: parseInt(record.total_code_lines_suggested),
          completion_acceptance_rate: parseInt(record.total_code_lines_accepted) / parseInt(record.total_code_lines_suggested)
        });
      }

      return acc;
    }, []);

    return NextResponse.json(aggregatedData);
  } catch (error) {
    console.error('Error reading completion team metrics:', error);
    return NextResponse.json({ error: 'Failed to load completion team metrics' }, { status: 500 });
  }
} 