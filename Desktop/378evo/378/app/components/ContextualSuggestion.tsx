import React from 'react';

interface ContextualSuggestionProps {
  suggestion: string;
  onDismiss: () => void;
}

const ContextualSuggestion: React.FC<ContextualSuggestionProps> = ({
  suggestion,
  onDismiss,
}) => {
  return (
    <div className="fixed bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 max-w-sm">
      <p>{suggestion}</p>
      <button onClick={onDismiss} className="absolute top-2 right-2" aria-label="Dismiss suggestion">
        x
      </button>
    </div>
  );
};

export default ContextualSuggestion;