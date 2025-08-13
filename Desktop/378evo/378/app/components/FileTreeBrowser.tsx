import React from 'react';

interface FileTreeBrowserProps {
  // This would be populated with actual file system data
  files: { name: string; type: 'file' | 'folder' }[];
}

const FileTreeBrowser: React.FC<FileTreeBrowserProps> = ({ files }) => {
  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem' }}>
      <h3>File Browser</h3>
      <ul>
        {files.map((file, index) => (
          <li key={index}>
            {file.type === 'folder' ? '📁' : '📄'} {file.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileTreeBrowser;