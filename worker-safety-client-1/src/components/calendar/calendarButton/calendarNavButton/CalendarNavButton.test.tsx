import { render, screen } from "@testing-library/react";
import CalendarNavButton from "./CalendarNavButton";

const mockOnClick = jest.fn();

describe(CalendarNavButton.name, () => {
  it('should render with the text "Last week" if "chevron_big_left" is set as the icon', () => {
    render(<CalendarNavButton icon="chevron_big_left" onClick={mockOnClick} />);
    screen.getByText("Last week");
  });

  it('should render with the text "Next week" if "chevron_big_right" is set as the icon', () => {
    render(
      <CalendarNavButton icon="chevron_big_right" onClick={mockOnClick} />
    );
    screen.getByText("Next week");
  });
});
