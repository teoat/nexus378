import type { Meta, StoryObj } from '@storybook/react';
import ColumnMappingInterface from '../components/ColumnMappingInterface';

const meta = {
  title: 'Example/ColumnMappingInterface',
  component: ColumnMappingInterface,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof ColumnMappingInterface>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    sourceColumns: ['Transaction ID', 'Date', 'Amount', 'Description'],
    targetFields: ['transactionId', 'date', 'amount', 'description'],
    onSubmit: () => {},
  },
};