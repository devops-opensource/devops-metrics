import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET() {
  try {
    const csvPath = path.join(process.cwd(), '../../notebooks/copilot_metrics_active_users.csv');
    const fileContents = await fs.readFile(csvPath, 'utf8');
    
    const records = parse(fileContents, {
      columns: true,
      skip_empty_lines: true
    });

    return NextResponse.json(records);
  } catch (error) {
    console.error('Error reading CSV file:', error);
    return NextResponse.json({ error: 'Failed to load metrics data' }, { status: 500 });
  }
} 