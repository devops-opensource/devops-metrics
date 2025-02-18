import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

interface ChatGlobalRecord {
  date: string;
  total_chat: string;
  total_engaged_users: string;
  total_chat_copy_events: string;
  total_chat_insertion_events: string;
  chat_per_user: string;
  chat_acceptance_rate: string;
}

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', '..', 'notebooks', 'copilot_metrics_chat_global.csv');
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    }) as ChatGlobalRecord[];

    // Transform to match TeamMetricsData interface
    const transformedRecords = records.map(record => ({
      team: 'Global',
      date: record.date,
      total_chat: record.total_chat,
      total_engaged_users: record.total_engaged_users,
      chat_acceptance_rate: parseFloat(record.chat_acceptance_rate),
      chat_per_user: parseFloat(record.chat_per_user),
      completion_acceptance_rate: 0 // Will be populated from completion data
    }));

    return NextResponse.json(transformedRecords);
  } catch (error) {
    console.error('Error reading global chat metrics:', error);
    return NextResponse.json({ error: 'Failed to load global chat metrics' }, { status: 500 });
  }
} 