import { Node, Edge } from 'reactflow';

export const initialNodes: Node[] = [
  {
    id: 'emp-1',
    type: 'default',
    data: { label: 'Employee: John Doe' },
    position: { x: 250, y: 5 },
  },
  {
    id: 'ven-1',
    type: 'default',
    data: { label: 'Vendor: JD Supplies Inc.' },
    position: { x: 100, y: 100 },
  },
  {
    id: 'ven-2',
    type: 'output',
    data: { label: 'Vendor: Global Corp' },
    position: { x: 400, y: 100 },
  },
  {
    id: 'bank-1',
    type: 'input',
    data: { label: 'Bank Account: ...xx1234' },
    position: { x: 250, y: 250 },
  },
];

export const initialEdges: Edge[] = [
  {
    id: 'e1-v1',
    source: 'emp-1',
    target: 'ven-1',
    label: 'Conflict of Interest',
    animated: true,
    style: { stroke: 'red', strokeWidth: 2 },
  },
  {
    id: 'e1-v2',
    source: 'emp-1',
    target: 'ven-2',
    label: 'Approved Payment'
  },
  {
    id: 'v1-b1',
    source: 'ven-1',
    target: 'bank-1',
    label: '$50,000 Payment'
  },
  {
    id: 'v2-b1',
    source: 'ven-2',
    target: 'bank-1',
    label: '$12,000 Payment'
  },
];
