import { NextRequest, NextResponse } from 'next/server';
import { ClientSecretCredential } from '@azure/identity';
import { ResourceManagementClient } from '@azure/arm-resources';

export async function GET(req: NextRequest) {
  const {
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
  } = process.env;

  if (!AZURE_TENANT_ID || !AZURE_CLIENT_ID || !AZURE_CLIENT_SECRET || !AZURE_SUBSCRIPTION_ID) {
    return NextResponse.json({ error: 'Missing Azure credentials' }, { status: 500 });
  }

  try {
    const credential = new ClientSecretCredential(
      AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET,
    );
    const rmClient = new ResourceManagementClient(credential, AZURE_SUBSCRIPTION_ID);

    // filtro opcional ?q=...
    const q = req.nextUrl.searchParams.get('q')?.toLowerCase() ?? '';

    const resources: {
      id: string;
      name: string;
      type: string;
      location: string;
      resourceGroup: string;
    }[] = [];

    // recorremos todos los RG
    for await (const rg of rmClient.resourceGroups.list()) {
      if (!rg.name) continue;

      for await (const res of rmClient.resources.listByResourceGroup(rg.name)) {
        if (!res.name || !res.type) continue;

        // aplica filtro en nombre o tipo
        if (
          q &&
          !res.name.toLowerCase().includes(q) &&
          !res.type.toLowerCase().includes(q)
        ) {
          continue;
        }

        resources.push({
          id: res.id ?? '',
          name: res.name,
          type: res.type,
          location: res.location ?? '',
          resourceGroup: rg.name,
        });
      }
    }

    return NextResponse.json({ resources });
  } catch (err: any) {
    return NextResponse.json(
      { error: 'Failed to fetch resources', details: err.message },
      { status: 500 },
    );
  }
}
