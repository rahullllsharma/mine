import { fireEvent, render, screen } from "@testing-library/react";
import PageFooter from "./PageFooter";

describe(PageFooter.name, () => {
  const mockPrimaryClick = jest.fn();

  it("should be rendered correctly", () => {
    const { asFragment } = render(
      <PageFooter primaryActionLabel="save" onPrimaryClick={mockPrimaryClick} />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should have the "onPrimaryClick" called when the action button is clicked', () => {
    render(
      <PageFooter primaryActionLabel="save" onPrimaryClick={mockPrimaryClick} />
    );
    const buttonElement = screen.getByRole("button", { name: /save/i });
    fireEvent.click(buttonElement);
    expect(mockPrimaryClick).toHaveBeenCalled();
  });

  it('button should be disabled if the "disabled" prop is passed', () => {
    render(
      <PageFooter
        primaryActionLabel="save"
        onPrimaryClick={mockPrimaryClick}
        isPrimaryActionDisabled
      />
    );
    const buttonElement = screen.getByRole("button", { name: /save/i });
    expect(buttonElement).toBeDisabled();
  });
});
