import { NextRequest, NextResponse } from 'next/server';

// Simple mock Fronius status for now
const mockFroniusStatus = {
  online: true,
  timestamp: new Date().toISOString(),
  mode: 'Enhanced Mock (Weather-Aware)',
  errorCount: 0
};

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json(mockFroniusStatus, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { 
        online: false, 
        error: 'Failed to get Fronius status',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    if (body.action === 'force_reconnect') {
      // Simulate reconnection
      return NextResponse.json({
        success: true,
        message: 'Reconnection successful',
        timestamp: new Date().toISOString()
      }, {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }
    
    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
} 