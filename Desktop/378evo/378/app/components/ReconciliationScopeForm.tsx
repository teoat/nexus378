import React, { useState } from 'react';

interface ReconciliationScopeFormProps {
  onSubmit: (scope: { type: string; value: string }) => void;
}

const ReconciliationScopeForm: React.FC<ReconciliationScopeFormProps> = ({ onSubmit }) => {
  const [scopeType, setScopeType] = useState('month');
  const [scopeValue, setScopeValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ type: scopeType, value: scopeValue });
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Reconciliation Scope</h2>
      <div className="mb-4">
        <label htmlFor="scopeType" className="block mb-2">Scope Type</label>
        <select
          id="scopeType"
          value={scopeType}
          onChange={(e) => setScopeType(e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="month">Month</option>
          <option value="trimester">Trimester</option>
          <option value="all">All Transactions</option>
        </select>
      </div>
      {scopeType !== 'all' && (
        <div className="mb-4">
          <label htmlFor="scopeValue" className="block mb-2">
            {scopeType === 'month' ? 'Month (e.g., July)' : 'Trimester (e.g., Q3)'}
          </label>
          <input
            type="text"
            id="scopeValue"
            value={scopeValue}
            onChange={(e) => setScopeValue(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
      )}
      <button type="submit" className="w-full p-2 bg-blue-500 text-white rounded" aria-label="Start reconciliation">
        Start Reconciliation
      </button>
    </form>
  );
};

export default ReconciliationScopeForm;