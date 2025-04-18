// src/app/api/jira/uninstalled/route.ts
import { NextResponse } from 'next/server';

export async function POST() {
  // podrías borrar el sharedSecret del Map si lo guardas en BD
  return NextResponse.json({ ok: true });
}
