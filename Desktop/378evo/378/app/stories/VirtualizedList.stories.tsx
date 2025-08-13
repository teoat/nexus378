import type { Meta, StoryObj } from '@storybook/react';
import { VirtualizedList } from '../components/VirtualizedList';
import AdjudicationPanel from '../components/AdjudicationPanel';
import { Transaction } from '@app/types';

const meta: Meta<typeof VirtualizedList> = {
  title: 'Components/VirtualizedList',
  component: VirtualizedList,
};

export default meta;
type Story = StoryObj<typeof VirtualizedList>;

// --- Story 1: Simple String List ---
const simpleItems = Array.from({ length: 10000 }, (_, i) => `Item #${i + 1}`);

export const SimpleList: Story = {
  args: {
    items: simpleItems,
    renderItem: (item: string) => (
      <div style={{ padding: '0 1rem', borderBottom: '1px solid #eee', height: '100%', display: 'flex', alignItems: 'center' }}>
        {item}
      </div>
    ),
    estimateSize: () => 35,
    height: '500px',
  },
};

// --- Story 2: Complex Component List ---
const mockTransactionPairs = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    transactionA: {
        id: BigInt(i * 2),
        transactionDate: new Date(),
        description: `Left Transaction #${i + 1}`,
        amount: 100 + i,
        currency: 'USD',
    } as Transaction,
    transactionB: {
        id: BigInt(i * 2 + 1),
        transactionDate: new Date(),
        description: `Right Transaction #${i + 1}`,
        amount: 100 + i,
        currency: 'USD',
    } as Transaction,
}));

export const AdjudicationPanelList: Story = {
    args: {
        items: mockTransactionPairs,
        renderItem: (item: (typeof mockTransactionPairs)[0]) => (
            <div style={{ padding: '0.5rem' }}>
                <AdjudicationPanel
                    transactionA={item.transactionA}
                    transactionB={item.transactionB}
                    onLink={() => { console.log('link clicked for item #', item.id)}}
                />
            </div>
        ),
        estimateSize: () => 250, // AdjudicationPanel is much taller
        height: '80vh',
    }
}