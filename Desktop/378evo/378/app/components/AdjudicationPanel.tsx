import React from 'react';

interface Transaction {
  id: string;
  date: string;
  amount: number;
  description: string;
}

interface AdjudicationPanelProps {
  transactionA: Transaction;
  transactionB: Transaction;
  onLink: () => void;
  onDismiss: () => void;
}

const AdjudicationPanel: React.FC<AdjudicationPanelProps> = ({
  transactionA,
  transactionB,
  onLink,
  onDismiss,
}) => {
  return (
    <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl w-full">
        <h2 className="text-2xl font-bold mb-4">Adjudication Panel</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="font-bold mb-2">Transaction A</h3>
            <p><strong>Date:</strong> {transactionA.date}</p>
            <p><strong>Amount:</strong> {transactionA.amount}</p>
            <p><strong>Description:</strong> {transactionA.description}</p>
          </div>
          <div>
            <h3 className="font-bold mb-2">Transaction B</h3>
            <p><strong>Date:</strong> {transactionB.date}</p>
            <p><strong>Amount:</strong> {transactionB.amount}</p>
            <p><strong>Description:</strong> {transactionB.description}</p>
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <button onClick={onDismiss} className="mr-2 p-2 bg-gray-200 rounded" aria-label="Dismiss adjudication">
            Dismiss
          </button>
          <button onClick={onLink} className="p-2 bg-blue-500 text-white rounded" aria-label="Link transactions">
            Link Transactions
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdjudicationPanel;