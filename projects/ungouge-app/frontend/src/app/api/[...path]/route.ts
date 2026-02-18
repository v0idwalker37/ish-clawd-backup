import { NextRequest } from 'next/server';
import { proxyRequest } from '@/lib/proxy';

// Catch-all proxy for any /api/* routes not handled by specific route handlers
export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/api/${params.path.join('/')}`;
  return proxyRequest(req, backendPath);
}

export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/api/${params.path.join('/')}`;
  return proxyRequest(req, backendPath);
}

export async function PUT(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/api/${params.path.join('/')}`;
  return proxyRequest(req, backendPath);
}

export async function DELETE(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/api/${params.path.join('/')}`;
  return proxyRequest(req, backendPath);
}

export async function PATCH(req: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/api/${params.path.join('/')}`;
  return proxyRequest(req, backendPath);
}
