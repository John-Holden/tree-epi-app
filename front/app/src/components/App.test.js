import { render, screen } from '@testing-library/react';
import SimulationPanel from './SimPanel';

test('renders learn react link', () => {
  render(<SimulationPanel />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
