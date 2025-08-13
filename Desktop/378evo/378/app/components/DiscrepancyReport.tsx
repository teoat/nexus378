import React from 'react';

interface Discrepancy {
  id: string;
  type: string;
  description: string;
  status: string;
}

interface DiscrepancyReportProps {
  discrepancies: Discrepancy[];
}

const DiscrepancyReport: React.FC<DiscrepancyReportProps> = ({ discrepancies }) => {
  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Discrepancy Report</h2>
      {discrepancies.length === 0 ? (
        <p>No discrepancies found.</p>
      ) : (
        <ul>
          {discrepancies.map((d) => (
            <li key={d.id} className="border-b py-2">
              <p><strong>Type:</strong> {d.type}</p>
              <p><strong>Description:</strong> {d.description}</p>
              <p><strong>Status:</strong> {d.status}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DiscrepancyReport;