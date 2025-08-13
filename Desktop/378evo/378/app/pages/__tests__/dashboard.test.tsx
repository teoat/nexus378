import { render, screen } from '@testing-library/react';
import Dashboard from '../dashboard';

describe('Dashboard', () => {
  it('renders a heading', () => {
    render(<Dashboard />);

    const heading = screen.getByRole('heading', {
      name: /live operations dashboard/i,
    });

    expect(heading).toBeInTheDocument();
  });
});