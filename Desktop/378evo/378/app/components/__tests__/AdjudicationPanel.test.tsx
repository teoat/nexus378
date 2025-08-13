import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import AdjudicationPanel, { AdjudicationPanelProps } from '../AdjudicationPanel';

// Mock data for our tests
const mockTransactionA = {
  id: 1n,
  transactionDate: new Date('2025-07-28'),
  description: 'Transaction A Description',
  amount: 100.50,
  currency: 'USD',
};

const mockTransactionB = {
  id: 2n,
  transactionDate: new Date('2025-07-29'),
  description: 'Transaction B Description',
  amount: 200.75,
  currency: 'USD',
};

describe('AdjudicationPanel', () => {
  // Test case 1: Does it render the data correctly?
  it('should render the details of both transactions', () => {
    // Arrange: Set up the props for our component
    const props: AdjudicationPanelProps = {
      transactionA: mockTransactionA,
      transactionB: mockTransactionB,
      onLink: jest.fn(), // jest.fn() creates a mock function
      isLoading: false,
    };

    // Act: Render the component with the props
    render(<AdjudicationPanel {...props} />);

    // Assert: Check if the data is visible on the screen
    // We check for the descriptions
    expect(screen.getByText('Transaction A Description')).toBeInTheDocument();
    expect(screen.getByText('Transaction B Description')).toBeInTheDocument();

    // We check for the amounts, formatted as they are in the component
    expect(screen.getByText('100.50 USD')).toBeInTheDocument();
    expect(screen.getByText('200.75 USD')).toBeInTheDocument();
  });

  // Test case 2: Is the button disabled initially?
  it('should have a disabled "Link Transactions" button when notes are empty', () => {
    // Arrange
    const props: AdjudicationPanelProps = {
      transactionA: mockTransactionA,
      transactionB: mockTransactionB,
      onLink: jest.fn(),
      isLoading: false,
    };

    // Act
    render(<AdjudicationPanel {...props} />);

    // Assert
    const linkButton = screen.getByRole('button', { name: /link transactions/i });
    expect(linkButton).toBeDisabled();
  });

  // Test case 3: Does typing in the notes enable the button?
  it('should enable the button when text is entered into the notes field', async () => {
    // Arrange
    const user = userEvent.setup();
    const props: AdjudicationPanelProps = {
      transactionA: mockTransactionA,
      transactionB: mockTransactionB,
      onLink: jest.fn(),
      isLoading: false,
    };
    render(<AdjudicationPanel {...props} />);
    const linkButton = screen.getByRole('button', { name: /link transactions/i });
    const notesTextArea = screen.getByRole('textbox', { name: /reconciliation notes/i });

    // Act
    await user.type(notesTextArea, 'These transactions are related.');

    // Assert
    expect(linkButton).toBeEnabled();
  });

  // Test case 4: Does clicking the button call onLink with the correct data?
  it('should call the onLink prop with the correct IDs and notes when clicked', async () => {
    // Arrange
    const user = userEvent.setup();
    const mockOnLink = jest.fn(); // Create a fresh mock function for this test
    const notesText = 'These transactions are definitely related.';
    const props: AdjudicationPanelProps = {
      transactionA: mockTransactionA,
      transactionB: mockTransactionB,
      onLink: mockOnLink, // Pass the mock function as a prop
      isLoading: false,
    };
    render(<AdjudicationPanel {...props} />);
    const linkButton = screen.getByRole('button', { name: /link transactions/i });
    const notesTextArea = screen.getByRole('textbox', { name: /reconciliation notes/i });

    // Act
    await user.type(notesTextArea, notesText);
    await user.click(linkButton);

    // Assert
    expect(mockOnLink).toHaveBeenCalledTimes(1); // Ensure it was called exactly once
    expect(mockOnLink).toHaveBeenCalledWith(
      mockTransactionA.id,
      mockTransactionB.id,
      notesText
    );
  });

  // Test case 5: Does it handle missing data gracefully?
  it('should render a clear message when transaction data is null', () => {
    // Arrange
    const mockIncompleteTransaction = {
      id: 3n,
      transactionDate: null,
      description: null,
      amount: null,
      currency: 'USD',
    };
    const props: AdjudicationPanelProps = {
      transactionA: mockIncompleteTransaction,
      transactionB: mockTransactionB,
      onLink: jest.fn(),
      isLoading: false,
    };

    // Act
    render(<AdjudicationPanel {...props} />);

    // Assert
    // Find all instances of the "Data Missing" text. We expect it for date, description, and amount.
    const missingMessages = screen.getAllByText('Data Missing');
    expect(missingMessages).toHaveLength(3);

    // Also, ensure the old "N/A" text is not present
    const oldMessage = screen.queryByText(/N\/A/i);
    expect(oldMessage).not.toBeInTheDocument();
  });
});