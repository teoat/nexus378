import React, { useState } from 'react';
import { ColumnMappingInterface } from '../components/ColumnMappingInterface';
import ReconciliationScopeForm from '../components/ReconciliationScopeForm';
import LiveReconciliationDashboard from '../components/LiveReconciliationDashboard';

const IngestionPage = () => {
  const [step, setStep] = useState(1);
  const [jobId, setJobId] = useState<string | null>(null);

  const handleMappingSubmit = () => {
    setStep(2);
  };

  const handleScopeSubmit = async (data: { scope: string; scopeValue: string }) => {
    // In a real application, you would make an API call here to start the job
    // and get a job ID back.
    const newJobId = `job-${Date.now()}`;
    setJobId(newJobId);
    setStep(3);
  };

  return (
    <div>
      <h1>Data Ingestion and Reconciliation</h1>
      {step === 1 && (
        <ColumnMappingInterface
          caseId="123" // This would be dynamic in a real app
          sourceColumns={['Date', 'Description', 'Amount', 'Branch Code']}
          targetFields={['transactionDate', 'description', 'amount']}
          onSubmit={handleMappingSubmit}
        />
      )}
      {step === 2 && <ReconciliationScopeForm onSubmit={handleScopeSubmit} />}
      {step === 3 && jobId && <LiveReconciliationDashboard jobId={jobId} />}
    </div>
  );
};

export default IngestionPage;