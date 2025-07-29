'use client';

import { useState } from 'react';
import styles from './ConnectionModal.module.css';

interface FroniusStatus {
  online: boolean;
  error?: string;
  timestamp?: string;
  mode?: string;
  errorCount?: number;
}

// Check if we're actually connected to real Fronius data
const isActuallyConnected = (froniusStatus: FroniusStatus | null) => {
  if (!froniusStatus) return false;
  // If it's a mock service, consider it as demo mode
  if (froniusStatus.mode && froniusStatus.mode.includes('Mock')) {
    return false;
  }
  return froniusStatus.online === true && !froniusStatus.error;
};

interface ConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  froniusStatus: FroniusStatus | null;
  isCheckingConnection: boolean;
  onForceReconnect: () => void;
  language: 'en' | 'ca';
}

export default function ConnectionModal({
  isOpen,
  onClose,
  froniusStatus,
  isCheckingConnection,
  onForceReconnect,
  language
}: ConnectionModalProps) {
  if (!isOpen) return null;

  const getConnectionStatusIcon = () => {
    if (!froniusStatus) return '🤖';
    
    if (isActuallyConnected(froniusStatus)) {
      return '🔌';
    }
    return '🤖';
  };

  const getConnectionStatusText = () => {
    if (!froniusStatus) {
      return language === 'ca' ? 'Versió Demo' : 'Demo Version';
    }
    
    if (isActuallyConnected(froniusStatus)) {
      return language === 'ca' ? 'Connectat' : 'Connected';
    } else {
      return language === 'ca' ? 'Versió Demo - Dades simulades' : 'Demo Version - Simulated data';
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>
            {isActuallyConnected(froniusStatus) 
              ? (language === 'ca' ? '🔌 Estat de Connexió' : '🔌 Connection Status')
              : (language === 'ca' ? '🤖 Versió Demo' : '🤖 Demo Version')
            }
          </h2>
          <button className={styles.closeButton} onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className={styles.modalBody}>
          <div className={styles.connectionStatus}>
            <div className={styles.statusIndicator}>
              {getConnectionStatusIcon()}
            </div>
            <div className={styles.statusInfo}>
              <div className={styles.statusTitle}>
                {language === 'ca' ? 'Inversors Fronius' : 'Fronius Inverter'}
              </div>
              <div className={styles.statusText}>
                {getConnectionStatusText()}
              </div>
              {froniusStatus && (
                <div className={styles.statusDetails}>
                  <span className={styles.hostInfo}>
                    {froniusStatus.online ? '192.168.1.128' : 'Offline'}
                  </span>
                  {froniusStatus.online && (
                    <span className={styles.responseTime}>
                      {language === 'ca' ? 'Resposta' : 'Response'}: {0}ms
                    </span>
                  )}
                  {froniusStatus.online && froniusStatus.error && (
                    <span className={styles.fallbackInfo}>
                      {language === 'ca' ? 'Error: ' + froniusStatus.error : 'Error: ' + froniusStatus.error}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {froniusStatus && (
            <div className={styles.connectionHealth}>
              <div className={styles.healthBar}>
                <div 
                  className={styles.healthFill}
                  style={{ 
                    width: isActuallyConnected(froniusStatus) ? '100%' : '0%',
                    backgroundColor: isActuallyConnected(froniusStatus) ? '#4CAF50' : '#F44336'
                  }}
                />
              </div>
              <span className={styles.healthText}>
                {language === 'ca' ? 'Salut del sistema' : 'System health'}: {isActuallyConnected(froniusStatus) ? 'Operacional' : 'Demo Mode'}
              </span>
            </div>
          )}
          
          <div className={styles.modalActions}>
            <button 
              className={styles.reconnectButton}
              onClick={onForceReconnect}
              disabled={isCheckingConnection}
            >
              {isCheckingConnection ? '🔄' : '🔌'} {language === 'ca' ? 'Reconnectar' : 'Reconnect'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 