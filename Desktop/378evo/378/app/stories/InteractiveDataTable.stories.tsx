import type { Meta, StoryObj } from '@storybook/react';
import InteractiveDataTableWithDefaultData from '../components/InteractiveDataTable';

const meta: Meta<typeof InteractiveDataTableWithDefaultData> = {
  title: 'Components/InteractiveDataTable',
  component: InteractiveDataTableWithDefaultData,
};

export default meta;
type Story = StoryObj<typeof InteractiveDataTableWithDefaultData>;

export const Default: Story = {
  args: {},
};