import React from 'react';
import { GraphVisualizer } from '@/components/GraphVisualizer';

const FraudGraphPage = () => {
  return (
    <div className="container mx-auto p-4 h-full">
      <h1 className="text-2xl font-bold mb-4">Fraud Graph Visualization</h1>
      <div className="w-full h-[80vh] border rounded-lg bg-gray-50">
        <GraphVisualizer />
      </div>
    </div>
  );
};

export default FraudGraphPage;
