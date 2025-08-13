import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import MultiStepForm from '../components/MultiStepForm';

const meta: Meta<typeof MultiStepForm> = {
  title: 'Components/MultiStepForm',
  component: MultiStepForm,
};

export default meta;
type Story = StoryObj<typeof MultiStepForm>;

const Step1 = () => <div>Step 1 Content</div>;
const Step2 = () => <div>Step 2 Content</div>;
const Step3 = () => <div>Step 3 Content</div>;

export const Default: Story = {
  args: {
    steps: [<Step1 />, <Step2 />, <Step3 />],
  },
};