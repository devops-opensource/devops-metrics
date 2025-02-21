import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

interface BillingRecord {
  total: string;
  inactive_this_cycle: string;
}

interface ActiveUsersRecord {
  date: string;
  total_active_users: string;
  total_engaged_users: string;
}

export async function GET() {
  try {
    // Obtain the total of license
    const csvPath = path.join(process.cwd(), '../../notebooks/copilot_metrics_billing_global.csv');
    const fileContents = await fs.readFile(csvPath, 'utf8');
    
    const billingRecords = parse(fileContents, {
      columns: true,
      skip_empty_lines: true
    }) as BillingRecord[];

    // Get the latest billing record
    const latestBillingRecord = billingRecords[billingRecords.length - 1];

    // Obtain the total of active users
    const activeUsersPath = path.join(process.cwd(), '../../notebooks/copilot_metrics_active_users.csv');
    const activeUsersFileContents = await fs.readFile(activeUsersPath, 'utf8');
    
    const activeUsersRecords = parse(activeUsersFileContents, {
      columns: true,
      skip_empty_lines: true
    }) as ActiveUsersRecord[];

    // Transform date strings to Date objects and combine with billing data
    const transformedRecords = activeUsersRecords.map((record) => ({
      extract_date: new Date(record.date),
      total: parseInt(latestBillingRecord.total || '0'),
      total_active_users: parseInt(record.total_active_users || '0'),
      total_engaged_users: parseInt(record.total_engaged_users || '0'),
      inactive_this_cycle: parseInt(latestBillingRecord.inactive_this_cycle || '0')
    }));

    return NextResponse.json(transformedRecords);
  } catch (error) {
    console.error('Erreur lors de la lecture du fichier CSV:', error);
    return NextResponse.json({ error: 'Échec du chargement des données métriques' }, { status: 500 });
  }
} 