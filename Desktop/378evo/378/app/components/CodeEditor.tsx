import React from 'react';

interface CodeEditorProps {
  code: string;
  language: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ code, language }) => {
  return (
    <pre style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '0.5rem', backgroundColor: '#f5f5f5' }}>
      <code>
        {code}
      </code>
    </pre>
  );
};

export default CodeEditor;