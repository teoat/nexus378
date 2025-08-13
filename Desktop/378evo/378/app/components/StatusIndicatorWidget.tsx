import React from 'react';

interface StatusIndicatorWidgetProps {
  serviceName: string;
  status: 'Online' | 'Degraded' | 'Offline';
}

const StatusIndicatorWidget: React.FC<StatusIndicatorWidgetProps> = ({ serviceName, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'Online':
        return 'green';
      case 'Degraded':
        return 'orange';
      case 'Offline':
        return 'red';
      default:
        return 'grey';
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem' }}>
      <h3>{serviceName}</h3>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: getStatusColor() }} />
        <span>{status}</span>
      </div>
    </div>
  );
};

export default StatusIndicatorWidget;