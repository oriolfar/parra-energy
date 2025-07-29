// getFlowColor.ts

export interface FlowColorInput {
  solar: number; // solar production in watts
  home: number;  // home consumption in watts
}

function lerpColor(hex1: string, hex2: string, t: number): string {
  const c1 = hexToRgb(hex1);
  const c2 = hexToRgb(hex2);
  if (!c1 || !c2) throw new Error('Invalid color for lerpColor');
  const r = Math.round(c1.r + (c2.r - c1.r) * t);
  const g = Math.round(c1.g + (c2.g - c1.g) * t);
  const b = Math.round(c1.b + (c2.b - c1.b) * t);
  return rgbToHex(r, g, b);
}

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const match = hex.replace('#', '').match(/.{1,2}/g);
  if (!match || match.length < 3) return { r: 0, g: 0, b: 0 };
  const [r, g, b] = match.map(x => parseInt(x, 16));
  return { r: r ?? 0, g: g ?? 0, b: b ?? 0 };
}

function rgbToHex(r: number, g: number, b: number): string {
  return (
    '#' +
    [r, g, b]
      .map(x => x.toString(16).padStart(2, '0'))
      .join('')
  );
}

export function getFlowColor({ solar, home }: FlowColorInput): string {
  if (home <= 0) return '#22c55e'; // If no consumption, default to green
  const solarRatio = Math.min(solar / home, 1);
  const excess = Math.max(solar - home, 0);
  const exportRatio = excess / home;
  let flowScore = Math.max(0, Math.min(solarRatio + exportRatio, 1));

  // Color stops
  const GREEN = '#22c55e';
  const YELLOW = '#facc15';
  const ORANGE = '#f97316';
  const RED = '#ef4444';

  if (flowScore >= 0.66) {
    // Green to Yellow
    const t = (flowScore - 0.66) / (1 - 0.66);
    return lerpColor(GREEN, YELLOW, 1 - t);
  } else if (flowScore >= 0.33) {
    // Yellow to Orange
    const t = (flowScore - 0.33) / (0.66 - 0.33);
    return lerpColor(YELLOW, ORANGE, 1 - t);
  } else {
    // Orange to Red
    const t = flowScore / 0.33;
    return lerpColor(ORANGE, RED, 1 - t);
  }
} 