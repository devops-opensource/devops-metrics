import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

interface LanguageRecord {
  team: string;
  date: string;
  language: string;
  total_code_lines_accepted: string;
  total_code_lines_suggested: string;
  completion_acceptance_rate: string;
}

interface AggregatedLanguageData {
  language: string;
  total_code_lines_suggested: number;
  total_code_lines_accepted: number;
  completion_acceptance_rate: number;
}

export async function GET(request: Request) {
  try {
    // Get team from query parameters
    const { searchParams } = new URL(request.url);
    const team = searchParams.get('team') || '';
    
    const filePath = path.join(process.cwd(), '..', '..', 'notebooks', 'copilot_metrics_completion_team.csv');
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    }) as LanguageRecord[];

    // Filter by team if provided
    const filteredRecords = team 
      ? records.filter(record => record.team === team)
      : records;

    // Aggregate data by language
    const languageMap = new Map<string, AggregatedLanguageData>();
    
    filteredRecords.forEach(record => {
      const language = record.language;
      const linesAccepted = parseInt(record.total_code_lines_accepted) || 0;
      const linesSuggested = parseInt(record.total_code_lines_suggested) || 0;
      
      if (languageMap.has(language)) {
        const existing = languageMap.get(language)!;
        existing.total_code_lines_accepted += linesAccepted;
        existing.total_code_lines_suggested += linesSuggested;
        existing.completion_acceptance_rate = 
          existing.total_code_lines_suggested > 0 
            ? existing.total_code_lines_accepted / existing.total_code_lines_suggested 
            : 0;
      } else {
        languageMap.set(language, {
          language,
          total_code_lines_accepted: linesAccepted,
          total_code_lines_suggested: linesSuggested,
          completion_acceptance_rate: linesSuggested > 0 ? linesAccepted / linesSuggested : 0
        });
      }
    });

    // Convert map to array and sort by total_code_lines_suggested in descending order
    const languageData = Array.from(languageMap.values())
      .sort((a, b) => b.total_code_lines_suggested - a.total_code_lines_suggested);

    return NextResponse.json(languageData);
  } catch (error) {
    console.error('Error reading language metrics:', error);
    return NextResponse.json({ error: 'Failed to load language metrics' }, { status: 500 });
  }
} 