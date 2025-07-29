'use client';

import React from 'react';
import styles from './PowerFlowCardPlus.module.css';

interface EnergyData {
  solarProduction: number; // in kW
  homeConsumption: number; // in kW
  gridImport: number; // in kW (positive = importing, negative = exporting)
}

interface PowerFlowCardPlusProps {
  energyData: EnergyData;
  language?: 'en' | 'cat'; // Language preference
}

const PowerFlowCardPlus: React.FC<PowerFlowCardPlusProps> = ({ energyData, language = 'en' }) => {
  const { solarProduction, homeConsumption, gridImport } = energyData;

  // Language translations
  const translations = {
    en: {
      solar: 'Solar',
      grid: 'Grid',
      home: 'Home',
      selling: 'Selling'
    },
    cat: {
      solar: 'Solar',
      grid: 'Xarxa', 
      home: 'Casa',
      selling: 'Venent a xarxa'
    }
  };

  const t = translations[language];
  
  // Calculate energy flows (exactly like the library)
  const solarToHome = Math.min(solarProduction, homeConsumption);
  const solarToGrid = Math.max(0, solarProduction - homeConsumption);
  const gridToHome = Math.max(0, homeConsumption - solarProduction);
  
  // Power flow card plus configuration defaults (like the library)
  const config = {
    min_flow_rate: 0.75,
    max_flow_rate: 6,
    max_expected_power: 2000, // watts
    min_expected_power: 0.01,
    use_new_flow_rate_model: true,
    disable_dots: false,
    // Tolerance settings - values below this threshold are set to 0
    display_zero_tolerance: {
      grid: 0, // Show all grid values (even 26W)
      solar: 0, // Show all solar values  
      battery: 0 // Show all battery values
    }
  };

  // Library's tolerance functions
  const isAboveTolerance = (value: number, tolerance: number): boolean => {
    return !!(value && value >= tolerance);
  };

  const adjustZeroTolerance = (value: number, tolerance: number): number => {
    if (!value) return 0;
    if (!tolerance) return value;
    return isAboveTolerance(value, tolerance) ? value : 0;
  };

  // Apply tolerance adjustments (like the library)
  const adjustedSolarToHome = adjustZeroTolerance(solarToHome, config.display_zero_tolerance.solar / 1000); // Convert W to kW
  const adjustedSolarToGrid = adjustZeroTolerance(solarToGrid, config.display_zero_tolerance.solar / 1000);
  const adjustedGridToHome = adjustZeroTolerance(gridToHome, config.display_zero_tolerance.grid / 1000);

  // Calculate percentages for flow labels
  const totalEnergyFlow = Math.max(adjustedSolarToHome + adjustedSolarToGrid + adjustedGridToHome, 0.001);
  const solarToHomePercent = Math.round((adjustedSolarToHome / totalEnergyFlow) * 100);
  const solarToGridPercent = Math.round((adjustedSolarToGrid / totalEnergyFlow) * 100);
  const gridToHomePercent = Math.round((adjustedGridToHome / totalEnergyFlow) * 100);

  // Library's flow rate calculation (new flow rate model)
  const computeFlowRate = (power: number): number => {
    const powerInWatts = power * 1000; // Convert kW to W
    const maxPower = config.max_expected_power;
    const minPower = config.min_expected_power;
    const maxRate = config.max_flow_rate;
    const minRate = config.min_flow_rate;
    
    if (powerInWatts > maxPower) return maxRate;
    return ((powerInWatts - minPower) * (maxRate - minRate)) / (maxPower - minPower) + minRate;
  };

  // Calculate durations (exactly like the library) using adjusted values
  const newDur = {
    solarToHome: computeFlowRate(adjustedSolarToHome),
    solarToGrid: computeFlowRate(adjustedSolarToGrid),
    gridToHome: computeFlowRate(adjustedGridToHome)
  };

  // Show line logic (like the library)
  const showLine = (power: number): boolean => {
    return power > 0; // Simplified - always show if power > 0
  };

  // Check if dots should show (like the library with tolerance)
  const shouldShowDots = (power: number, toleranceKW: number): boolean => {
    return !config.disable_dots && power > 0 && power >= toleranceKW;
  };

  const formatPower = (value: number): string => {
    if (value >= 1) {
      return `${value.toFixed(1)} kW`;
    }
    return `${Math.round(value * 1000)} W`;
  };

  // Calculate circumferences for percentage circles (like the library)
  const circleCircumference = 238.76104; // Full circle circumference
  
  // Home energy sources percentages
  const totalHomeConsumption = Math.max(adjustedGridToHome + adjustedSolarToHome, 0.001); // Avoid division by zero
  const homeSolarCircumference = adjustedSolarToHome > 0 ? circleCircumference * (adjustedSolarToHome / totalHomeConsumption) : 0;
  const homeGridCircumference = adjustedGridToHome > 0 ? circleCircumference * (adjustedGridToHome / totalHomeConsumption) : 0;
  
  // Solar energy distribution percentages  
  const totalSolarProduction = Math.max(adjustedSolarToHome + adjustedSolarToGrid, 0.001);
  const solarToHomeCircumference = adjustedSolarToHome > 0 ? circleCircumference * (adjustedSolarToHome / totalSolarProduction) : 0;
  const solarToGridCircumference = adjustedSolarToGrid > 0 ? circleCircumference * (adjustedSolarToGrid / totalSolarProduction) : 0;

  // Map a percentage (0-100) to a dot radius (min 2px, max 10px)
  const getDotRadius = (percent: number) => {
    const minR = 2;
    const maxR = 10;
    return minR + ((maxR - minR) * (percent / 100));
  };

  // Determine scenario for background color
  function getEnergyScenario(solarToHome: number, solarToGrid: number, gridToHome: number) {
    if (solarToGrid > 0 && solarToHome > 0 && gridToHome === 0) return 'selling'; // Green
    if (solarToGrid === 0 && solarToHome > 0 && gridToHome === 0) return 'solarOnly'; // Yellow
    if (solarToHome > 0 && gridToHome > 0) return 'mix'; // Orange
    if (solarToHome === 0 && gridToHome > 0) return 'gridOnly'; // Red
    return 'unknown';
  }
  const scenario = getEnergyScenario(adjustedSolarToHome, adjustedSolarToGrid, adjustedGridToHome);

  return (
    <div className={`${styles.powerFlowContainer}`}>
      <svg className={styles.flowSvg} viewBox="0 0 400 300" preserveAspectRatio="xMidYMid meet">
        <defs>
          {/* Single path definitions for both animation and display */}
          <path
  id="solar-home"
  d="M 235 90 Q 310 125 335 155"
  fill="none"
/>
<path
  id="solar-grid"
  d="M 165 90 Q 90 125 65 155"
  fill="none"
/>
<path
  id="grid-home"
  d="M 85 185 L 315 185"
  fill="none"
/>
        </defs>

        {/* Solar to Home Flow */}
        {showLine(adjustedSolarToHome) && (
          <>
            <use
              href="#solar-home"
              className={`${styles.flowPath} ${styles.solar}`}
              vectorEffect="non-scaling-stroke"
            />
            {shouldShowDots(adjustedSolarToHome, config.display_zero_tolerance.solar / 1000) && (
              <circle
                r={getDotRadius(solarToHomePercent)}
                className={`${styles.flowDot} ${styles.solar}`}
                vectorEffect="non-scaling-stroke"
              >
                <animateMotion
                  dur={`${newDur.solarToHome}s`}
                  repeatCount="indefinite"
                  calcMode="linear"
                >
                  <mpath href="#solar-home" />
                </animateMotion>
              </circle>
            )}
            <text
              x="295"
              y="115"
              className={styles.flowLabel}
              textAnchor="middle"
            >
              {solarToHomePercent}%
            </text>
          </>
        )}

        {/* Solar to Grid Flow */}
        {showLine(adjustedSolarToGrid) && (
          <>
            <use
              href="#solar-grid"
              className={`${styles.flowPath} ${styles.solarToGrid}`}
              vectorEffect="non-scaling-stroke"
            />
            {shouldShowDots(adjustedSolarToGrid, config.display_zero_tolerance.solar / 1000) && (
              <circle
                r={getDotRadius(solarToGridPercent)}
                className={`${styles.flowDot} ${styles.solarToGrid}`}
                vectorEffect="non-scaling-stroke"
              >
                <animateMotion
                  dur={`${newDur.solarToGrid}s`}
                  repeatCount="indefinite"
                  calcMode="linear"
                >
                  <mpath href="#solar-grid" />
                </animateMotion>
              </circle>
            )}
            <text
              x="105"
              y="115"
              className={styles.flowLabel}
              textAnchor="middle"
            >
              {solarToGridPercent}%
            </text>
          </>
        )}

        {/* Grid to Home Flow */}
        {showLine(adjustedGridToHome) && (
          <>
            <use
              href="#grid-home"
              className={`${styles.flowPath} ${styles.grid}`}
              vectorEffect="non-scaling-stroke"
            />
            {shouldShowDots(adjustedGridToHome, config.display_zero_tolerance.grid / 1000) && (
              <circle
                r={getDotRadius(gridToHomePercent)}
                className={`${styles.flowDot} ${styles.grid}`}
                vectorEffect="non-scaling-stroke"
              >
                <animateMotion
                  dur={`${newDur.gridToHome}s`}
                  repeatCount="indefinite"
                  calcMode="linear"
                >
                  <mpath href="#grid-home" />
                </animateMotion>
              </circle>
            )}
            <text
              x="200"
              y="175"
              className={styles.flowLabel}
              textAnchor="middle"
            >
              {gridToHomePercent}%
            </text>
          </>
        )}
      </svg>

      {/* Energy Nodes */}
      <div className={styles.nodeContainer}>
        {/* Solar Node - Top Center */}
        <div className={`${styles.energyNode} ${styles.solarNode}`}>
          <div className={styles.nodeIcon}>☀️</div>
          <div className={styles.nodeValue}>{formatPower(solarProduction)}</div>
          <div className={styles.nodeLabel}>{t.solar}</div>
          {/* Solar distribution circles (like the library) */}
          <svg className={styles.nodeCircleSections} viewBox="0 0 80 80">
            {solarToHomeCircumference > 0 && (
              <circle
                className={`${styles.solarCircle} ${styles.solarToHome}`}
                cx="40"
                cy="40"
                r="38"
                strokeDasharray={`${solarToHomeCircumference} ${circleCircumference - solarToHomeCircumference}`}
                strokeDashoffset={`-${circleCircumference - solarToHomeCircumference}`}
              />
            )}
            {solarToGridCircumference > 0 && (
              <circle
                className={`${styles.solarCircle} ${styles.solarToGrid}`}
                cx="40"
                cy="40"
                r="38"
                strokeDasharray={`${solarToGridCircumference} ${circleCircumference - solarToGridCircumference}`}
                strokeDashoffset={`-${circleCircumference - solarToGridCircumference - solarToHomeCircumference}`}
              />
            )}
          </svg>
        </div>

        {/* Grid Node - Middle Left */}
        <div className={`${styles.energyNode} ${styles.gridNode} ${gridImport > 0 ? styles.gridBuying : styles.gridSelling}`}>
          <div className={styles.nodeIcon}>⚡</div>
          <div className={styles.nodeValue}>{formatPower(Math.abs(gridImport))}</div>
          <div className={styles.nodeLabel}>{t.grid}</div>
        </div>

        {/* Home Node - Middle Right */}
        <div className={`${styles.energyNode} ${styles.homeNode}`}>
          <div className={styles.nodeIcon}>🏠</div>
          <div className={styles.nodeValue}>{formatPower(homeConsumption)}</div>
          <div className={styles.nodeLabel}>{t.home}</div>
          {/* Home sources circles (like the library) */}
          <svg className={styles.nodeCircleSections} viewBox="0 0 80 80">
            {homeSolarCircumference > 0 && (
              <circle
                className={`${styles.homeCircle} ${styles.homeSolar}`}
                cx="40"
                cy="40"
                r="38"
                strokeDasharray={`${homeSolarCircumference} ${circleCircumference - homeSolarCircumference}`}
                strokeDashoffset={`-${circleCircumference - homeSolarCircumference}`}
              />
            )}
            {homeGridCircumference > 0 && (
              <circle
                className={`${styles.homeCircle} ${styles.homeGrid}`}
                cx="40"
                cy="40"
                r="38"
                strokeDasharray={`${homeGridCircumference} ${circleCircumference - homeGridCircumference}`}
                strokeDashoffset={`-${circleCircumference - homeGridCircumference - homeSolarCircumference}`}
              />
            )}
          </svg>
        </div>
      </div>
    </div>
  );
};

export default PowerFlowCardPlus; 