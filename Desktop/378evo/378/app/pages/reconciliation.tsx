import React, { useState } from 'react';
import { VirtualizedList } from '../components/VirtualizedList';
import AdjudicationPanel from '../components/AdjudicationPanel';
import { Transaction } from '@app/types';
import { useNotifications } from '../hooks/useNotifications';

// Mock data generation - in a real app, this would come from an API
const generateMockData = () => Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    transactionA: {
        id: BigInt(i * 2),
        transactionDate: new Date(),
        description: `Left Transaction #${i + 1}`,
        amount: 100 + i,
        currency: 'USD',
    } as Transaction,
    transactionB: {
        id: BigInt(i * 2 + 1),
        transactionDate: new Date(),
        description: `Right Transaction #${i + 1}`,
        amount: 100 + i,
        currency: 'USD',
    } as Transaction,
}));

const ReconciliationPage = () => {
  const toast = useNotifications();
  const [transactionPairs, setTransactionPairs] = useState(generateMockData);

  const handleLinkTransactions = (id: number) => {
    // --- This is the Optimistic UI Update ---
    // 1. Keep a copy of the old data in case we need to revert.
    const originalPairs = [...transactionPairs];
    
    // 2. Immediately update the UI by removing the linked item.
    setTransactionPairs(currentPairs => currentPairs.filter(p => p.id !== id));
    toast.success('Transactions linked!');

    // 3. Make the real API call in the background.
    // fakeApiCall(id).catch(() => {
    //   // 4. If the API call fails, revert the UI and show an error.
    //   setTransactionPairs(originalPairs);
    //   toast.error('Failed to link transactions. Please try again.');
    // });
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Reconciliation Workbench</h1>
      <p className="mb-4">Displaying {transactionPairs.length.toLocaleString()} pairs for adjudication.</p>
      <div className="border rounded-lg">
        <VirtualizedList
            items={transactionPairs}
            renderItem={(item) => (
                <div style={{ padding: '0.5rem' }}>
                    <AdjudicationPanel
                        transactionA={item.transactionA}
                        transactionB={item.transactionB}
                        onLink={() => handleLinkTransactions(item.id)}
                    />
                </div>
            )}
            estimateSize={() => 250}
            height="80vh"
        />
      </div>
    </div>
  );
};

export default ReconciliationPage;