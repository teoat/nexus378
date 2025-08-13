import type { Meta, StoryObj } from '@storybook/react';
import AdjudicationPanel from '../components/AdjudicationPanel';

const meta = {
  title: 'Example/AdjudicationPanel',
  component: AdjudicationPanel,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof AdjudicationPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    transactionA: {
      id: '1',
      date: '2025-08-03',
      amount: 100,
      description: 'Transaction A',
    },
    transactionB: {
      id: '2',
      date: '2025-08-03',
      amount: 100,
      description: 'Transaction B',
    },
    onLink: () => {},
    onDismiss: () => {},
  },
};