// src/app/api/jira/installed/route.ts
import { NextResponse } from 'next/server';

interface InstallPayload {
  clientKey: string;
  sharedSecret: string;
  baseUrl: string;
  productType: string;
  description: string;
  oauthClientId: string;
  userKey: string;
}

const installations = new Map<string, string>(); // <clientKey, sharedSecret>

export async function POST(req: Request) {
  const body = (await req.json()) as InstallPayload;
  installations.set(body.clientKey, body.sharedSecret);
  console.log('✅ Jira site installed →', body.baseUrl);
  return NextResponse.json({ ok: true });
}
