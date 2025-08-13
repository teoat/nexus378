import React from 'react';
import { StoryFn, Meta } from '@storybook/react';
import Report from '../components/Report';
import { ComponentProps } from 'react';

export default {
  title: 'Components/Report',
  component: Report,
} as Meta;

const Template: StoryFn<ComponentProps<typeof Report>> = (args) => <Report {...args} />;

export const Default = Template.bind({});
Default.args = {
  report: {
    id: '1',
    name: 'Test Report',
    description: 'This is a test report.',
    configuration: {
      charts: [
        { type: 'bar', data: [1, 2, 3] },
        { type: 'line', data: [4, 5, 6] },
      ],
    },
  },
};