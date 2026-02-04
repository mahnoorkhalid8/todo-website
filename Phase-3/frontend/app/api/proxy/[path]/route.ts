import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// This API route acts as a proxy to forward requests to the backend
export async function GET(request: NextRequest) {
  return handleRequest(request);
}

export async function POST(request: NextRequest) {
  return handleRequest(request);
}

export async function PUT(request: NextRequest) {
  return handleRequest(request);
}

export async function DELETE(request: NextRequest) {
  return handleRequest(request);
}

async function handleRequest(request: NextRequest) {
  // Construct the backend URL
  const BACKEND_URL = process.env.BACKEND_URL || 'https://mahnoorkhalid8-todo-bot.hf.space';

  // Get the path after /api/proxy/
  const url = new URL(request.url);
  const path = url.pathname.replace('/api/proxy/', '');

  // Construct the full backend URL
  const backendUrl = `${BACKEND_URL}/${path}${url.search}`;

  try {
    // Get the request body if it exists
    let body = null;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      body = await request.json();
    }

    // Forward the request to the backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('authorization') || '',
        'Accept': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    // Get response headers and remove problematic ones
    const responseHeaders = new Map(response.headers.entries());

    // Create the response with the data
    const data = await response.json();

    // Create new headers for the response
    const newHeaders = new Headers();
    responseHeaders.forEach((value, key) => {
      if (key.toLowerCase() !== 'transfer-encoding') {
        newHeaders.set(key, value);
      }
    });

    return NextResponse.json(data, {
      status: response.status,
      headers: newHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Proxy error', message: (error as Error).message },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';