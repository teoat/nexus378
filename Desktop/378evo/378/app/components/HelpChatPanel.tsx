import React, { useState } from 'react';

interface Message {
  text: string;
  sender: 'user' | 'agent';
}

const HelpChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
      // Here you would send the message to the HelpAgent
    }
  };

  return (
    <div className="fixed bottom-20 right-4 bg-white rounded-lg shadow-lg w-80 h-96 flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">Help</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : ''}`}>
            <span className={`inline-block p-2 rounded-lg ${msg.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <div className="p-4 border-t flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 p-2 border rounded-l-lg"
          placeholder="Ask a question..."
          title="Ask a question"
          aria-label="Ask a question"
        />
        <button onClick={handleSend} className="p-2 bg-blue-500 text-white rounded-r-lg" aria-label="Send message">
          Send
        </button>
      </div>
    </div>
  );
};

export default HelpChatPanel;