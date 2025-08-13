import React from 'react';

interface DiffViewerProps {
  oldCode: string;
  newCode: string;
}

const DiffViewer: React.FC<DiffViewerProps> = ({ oldCode, newCode }) => {
  // This is a simplified diff viewer. A real implementation would use a library like diff2html.
  return (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <pre style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem', backgroundColor: '#f5f5f5', width: '50%' }}>
        <code>
          {oldCode}
        </code>
      </pre>
      <pre style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem', backgroundColor: '#f5f5f5', width: '50%' }}>
        <code>
          {newCode}
        </code>
      </pre>
    </div>
  );
};

export default DiffViewer;