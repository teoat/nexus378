import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface MatchResult {
  id: string;
  transactionA: any;
  transactionB: any;
  rationale: string;
}

const LiveReconciliationDashboard: React.FC = () => {
  const [matched, setMatched] = useState<MatchResult[]>([]);
  const [unmatched, setUnmatched] = useState<any[]>([]);
  const { socket } = useWebSocket();

  useEffect(() => {
    if (!socket) return;

    const handleMatch = (result: MatchResult) => {
      setMatched((prev) => [result, ...prev]);
    };

    const handleUnmatch = (transaction: any) => {
      setUnmatched((prev) => [transaction, ...prev]);
    };

    socket.on('match-result', handleMatch);
    socket.on('unmatch-result', handleUnmatch);

    return () => {
      socket.off('match-result', handleMatch);
      socket.off('unmatch-result', handleUnmatch);
    };
  }, [socket]);

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Live Reconciliation Feed</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="font-bold mb-2">Matched Transactions</h3>
          <ul>
            {matched.map((m) => (
              <li key={m.id} className="border-b py-2">
                <p><strong>Rationale:</strong> {m.rationale}</p>
                {/* Display transaction details here */}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-2">Unmatched Transactions</h3>
          <ul>
            {unmatched.map((t) => (
              <li key={t.id} className="border-b py-2">
                {/* Display transaction details here */}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LiveReconciliationDashboard;