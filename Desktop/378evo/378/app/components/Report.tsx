import React from 'react';

interface ReportProps {
  report: {
    id: string;
    name: string;
    description: string;
    configuration: any;
  };
}

const replacer = (key: any, value: any) =>
  typeof value === 'bigint' ? value.toString() : value;

const Report: React.FC<ReportProps> = ({ report }) => {
  return (
    <div>
      <h2>{report.name}</h2>
      <p>{report.description}</p>
      <pre>{JSON.stringify(report.configuration, replacer, 2)}</pre>
    </div>
  );
};

export default Report;