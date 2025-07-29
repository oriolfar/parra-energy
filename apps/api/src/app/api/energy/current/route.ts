import { NextRequest, NextResponse } from 'next/server';

// Mock energy data generator
function generateMockEnergyData() {
  const now = new Date();
  const minutesSinceStart = Math.floor(now.getTime() / (1000 * 60));
  const scenario = minutesSinceStart % 40; // Change scenario every 10 minutes (4 scenarios × 10 min)

  let solarProduction: number;
  let consumption: number;
  let gridPower: number;

  if (scenario < 10) {
    // Scenario 1: High solar, low consumption (selling to grid)
    solarProduction = 4500 + Math.random() * 1000;
    consumption = 1500 + Math.random() * 500;
    gridPower = -(solarProduction - consumption); // Negative = selling
  } else if (scenario < 20) {
    // Scenario 2: Solar covers most consumption
    solarProduction = 2500 + Math.random() * 500;
    consumption = 2000 + Math.random() * 700;
    gridPower = Math.max(0, consumption - solarProduction);
  } else if (scenario < 30) {
    // Scenario 3: Low solar, high consumption (buying from grid)
    solarProduction = 800 + Math.random() * 400;
    consumption = 3000 + Math.random() * 800;
    gridPower = consumption - solarProduction;
  } else {
    // Scenario 4: No solar (night time), 100% grid consumption
    solarProduction = 0;
    consumption = 2200 + Math.random() * 600;
    gridPower = consumption;
  }

  return {
    solarProduction: Math.round(solarProduction),
    consumption: Math.round(consumption),
    gridPower: Math.round(gridPower),
    timestamp: now.toISOString(),
    scenario: Math.floor(scenario / 10) + 1
  };
}

export async function GET(request: NextRequest) {
  try {
    const energyData = generateMockEnergyData();
    
    return NextResponse.json(energyData, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch energy data' },
      { status: 500 }
    );
  }
} 