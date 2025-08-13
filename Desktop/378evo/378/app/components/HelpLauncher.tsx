import React, { useState } from 'react';
import HelpChatPanel from './HelpChatPanel';

const HelpLauncher: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-blue-500 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg"
        aria-label="Open help panel"
      >
        ?
      </button>
      {isOpen && <HelpChatPanel />}
    </div>
  );
};

export default HelpLauncher;