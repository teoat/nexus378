import React from 'react';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Account 1' } },
  { id: '2', position: { x: 0, y: 100 }, data: { label: 'Transaction' } },
  { id: '3', position: { x: 200, y: 100 }, data: { label: 'Account 2' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
];

export function GraphVisualizer() {
  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}