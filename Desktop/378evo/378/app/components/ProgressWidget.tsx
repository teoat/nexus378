import React from 'react';
import { useWebSocket } from './WebSocketProvider';

interface ProgressWidgetProps {
  jobName: string;
  caseId: string; // We now identify progress by caseId
}

const ProgressWidget: React.FC<ProgressWidgetProps> = ({ jobName, caseId }) => {
  const { progress } = useWebSocket();
  const currentProgress = progress.get(caseId) || 0;
  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem' }}>
      <h3>{jobName}</h3>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <progress value={currentProgress} max="100" style={{ width: '100%' }} />
        <span>{currentProgress}%</span>
      </div>
    </div>
  );
};

export default ProgressWidget;