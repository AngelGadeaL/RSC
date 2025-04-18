import { NextResponse } from 'next/server';
import { ClientSecretCredential } from '@azure/identity';
import { ResourceManagementClient } from '@azure/arm-resources';

export async function GET() {
  const {
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
  } = process.env;

  if (!AZURE_TENANT_ID || !AZURE_CLIENT_ID || !AZURE_CLIENT_SECRET || !AZURE_SUBSCRIPTION_ID) {
    return NextResponse.json({ error: 'Missing Azure credentials' }, { status: 500 });
  }

  const credential = new ClientSecretCredential(
    AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET,
  );
  const rmClient = new ResourceManagementClient(credential, AZURE_SUBSCRIPTION_ID);

  const groups = [];
  for await (const g of rmClient.resourceGroups.list()) {
    groups.push({ id: g.id ?? '', name: g.name ?? '', location: g.location ?? '' });
  }

  return NextResponse.json({ groups });
}
