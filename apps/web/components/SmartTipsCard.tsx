'use client';

import styles from './SmartTipsCard.module.css';

interface SmartTip {
  type: 'weather' | 'opportunity' | 'timing' | 'optimization' | 'maintenance' | 'seasonal' | 'emergency' | 'efficiency';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  title: string;
  message: string;
  action: string;
}

interface SmartTipsCardProps {
  tips: SmartTip[];
  language: 'en' | 'ca';
}

export default function SmartTipsCard({ tips, language }: SmartTipsCardProps) {
  // Always show exactly 3 tips
  const displayTips = tips.slice(0, 3);
  
  // If we don't have 3 tips, add fallback tips
  const fallbackTips: SmartTip[] = [
    {
      type: 'optimization',
      priority: 'medium',
      icon: '💡',
      title: language === 'ca' ? 'Consell General Solar' : 'General Solar Tip',
      message: language === 'ca'
        ? 'Els panells solars funcionen millor entre les 10:00 i les 16:00 hores.'
        : 'Solar panels work best between 10:00 AM and 4:00 PM.',
      action: language === 'ca' ? 'Utilitzeu electrodomèstics en aquestes hores' : 'Use appliances during these hours'
    },
    {
      type: 'timing',
      priority: 'medium',
      icon: '⏰',
      title: language === 'ca' ? 'Programació Intel·ligent' : 'Smart Scheduling',
      message: language === 'ca'
        ? 'Programeu electrodomèstics durant les hores de màxima producció solar.'
        : 'Schedule appliances during peak solar production hours.',
      action: language === 'ca' ? 'Programeu tasques per les 12:00-15:00' : 'Schedule tasks for 12:00-15:00'
    },
    {
      type: 'optimization',
      priority: 'low',
      icon: '🔋',
      title: language === 'ca' ? 'Carregar Dispositius' : 'Charge Devices',
      message: language === 'ca'
        ? 'Carregueu telèfons i tablets durant les hores de sol per充分利用 l\'energia gratuïta.'
        : 'Charge phones and tablets during sunny hours to use free energy.',
      action: language === 'ca' ? 'Carregueu ara si hi ha sol' : 'Charge now if sunny'
    }
  ];

  // Ensure we always have exactly 3 tips
  let finalTips = displayTips;
  if (displayTips.length < 3) {
    finalTips = [...displayTips, ...fallbackTips.slice(0, 3 - displayTips.length)];
  }
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#ef4444'; // Red for urgent
      case 'medium': return '#f59e0b'; // Orange for important
      case 'low': return '#10b981'; // Green for info
      default: return '#6b7280'; // Gray for default
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'weather': return '🌤️';
      case 'opportunity': return '💡';
      case 'timing': return '⏰';
      case 'optimization': return '⚡';
      case 'maintenance': return '🔧';
      case 'seasonal': return '🌱';
      case 'emergency': return '🚨';
      case 'efficiency': return '📊';
      default: return '💡';
    }
  };

  if (finalTips.length === 0) {
    return (
      <div className={styles.smartTipsCard}>
        <h3 className={styles.smartTipsTitle}>
          {language === 'ca' ? '💡 CONSELLS INTEL·LIGENTS' : '💡 SMART TIPS'}
        </h3>
        <div className={styles.noTips}>
          {language === 'ca' 
            ? 'Carregant consells...' 
            : 'Loading tips...'
          }
        </div>
      </div>
    );
  }

  return (
    <div className={styles.smartTipsCard}>
      <h3 className={styles.smartTipsTitle}>
        {language === 'ca' ? '💡 CONSELLS INTEL·LIGENTS' : '💡 SMART TIPS'}
      </h3>
      <div className={styles.tipsContainer}>
        {finalTips.map((tip, index) => (
          <div 
            key={index} 
            className={`${styles.tipCard} ${styles[`tip-${tip.priority}`]}`}
            style={{
              borderLeftColor: getPriorityColor(tip.priority),
              borderLeftWidth: '4px',
              borderLeftStyle: 'solid'
            }}
          >
            <div className={styles.tipHeader}>
              <div className={styles.tipIcon}>{tip.icon}</div>
              <div className={styles.tipTypeIcon}>{getTypeIcon(tip.type)}</div>
              <div className={styles.tipPriority} style={{ backgroundColor: getPriorityColor(tip.priority) }}>
                {tip.priority === 'high' ? (language === 'ca' ? 'URGENT' : 'URGENT') :
                 tip.priority === 'medium' ? (language === 'ca' ? 'IMPORTANT' : 'IMPORTANT') :
                 language === 'ca' ? 'INFO' : 'INFO'}
              </div>
            </div>
            <div className={styles.tipContent}>
              <div className={styles.tipTitle}>{tip.title}</div>
              <div className={styles.tipMessage}>{tip.message}</div>
              <div className={styles.tipAction}>
                <span className={styles.actionIcon}>👉</span>
                {tip.action}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 