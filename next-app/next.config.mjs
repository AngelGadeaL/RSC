/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    AZURE_TENANT_ID: process.env.AZURE_TENANT_ID,
    AZURE_CLIENT_ID: process.env.AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET: process.env.AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID: process.env.AZURE_SUBSCRIPTION_ID,
  },
};

export default nextConfig; 