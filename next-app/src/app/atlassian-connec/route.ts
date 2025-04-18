// src/app/atlassian-connect/route.ts
import { NextResponse } from 'next/server';
import descriptor from '../../../atlassian-connect.json' assert { type: 'json' };

export async function GET(request: Request) {
  const host = `${request.headers.get('x-forwarded-proto') ?? 'http'}://${request.headers.get('host')}`;
  const desc = JSON.parse(JSON.stringify(descriptor).replace('{{HOST}}', host));
  return NextResponse.json(desc);
}
