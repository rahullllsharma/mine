import { render, screen, fireEvent } from "@testing-library/react";
import CalendarButton from "./CalendarButton";

const mockOnClick = jest.fn();

describe(CalendarButton.name, () => {
  it("should render a default calendar button", () => {
    const { asFragment } = render(<CalendarButton onClick={mockOnClick} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render with a blue border when "isToday" is set to true', () => {
    const { asFragment } = render(
      <CalendarButton onClick={mockOnClick} isToday />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render with a ticker and darker border when "isActive" is set to true', () => {
    const { asFragment } = render(
      <CalendarButton onClick={mockOnClick} isActive />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render with a ticker and blue border when "isActive" and "isToday" are set to true', () => {
    const { asFragment } = render(
      <CalendarButton onClick={mockOnClick} isActive isToday />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should be disabled when "isDisabled" is set to true', () => {
    render(<CalendarButton onClick={mockOnClick} isDisabled />);
    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toBeDisabled();
  });

  it('should call the "mockOnClick" callback when "onClick" event is triggered', () => {
    render(<CalendarButton onClick={mockOnClick} />);
    const buttonElement = screen.getByRole("button");
    fireEvent.click(buttonElement);
    expect(mockOnClick).toBeCalled();
  });
});
