import { render, screen } from "@testing-library/react";
import CalendarDayButton from "./CalendarDayButton";

const mockOnClick = jest.fn();

describe(CalendarDayButton.name, () => {
  it("should render a calendar day button", () => {
    const { asFragment } = render(
      <CalendarDayButton date="2020-01-19" onClick={mockOnClick} />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render with the text matching the day and weekday of the "date" prop', () => {
    render(<CalendarDayButton date="2022-01-20" onClick={mockOnClick} />);
    screen.getByText("20");
    screen.getByText("Thu");
  });

  it("should render a day with a lighter blue color if the date is today", () => {
    const today = new Date().toString();
    const day = new Date(today).toLocaleDateString("en-US", { day: "numeric" });
    render(<CalendarDayButton date={today} onClick={mockOnClick} />);
    const dayElement = screen.getByText(day);
    expect(dayElement).toHaveClass("text-brand-urbint-40");
  });

  it("should render without text content if an invalid date is passed", () => {
    const { asFragment } = render(
      <CalendarDayButton date="invalid date" onClick={mockOnClick} />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
