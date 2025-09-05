import { fireEvent, render, screen } from "@testing-library/react";
import Checkbox from "./Checkbox";

describe(Checkbox.name, () => {
  it("should render correctly", () => {
    const { asFragment } = render(<Checkbox />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("should accept a default value", () => {
    render(<Checkbox defaultChecked />);
    screen.getByRole("checkbox", { checked: true });
  });

  it("should trigger an onChange event when clicked", () => {
    const mockOnChange = jest.fn();
    render(<Checkbox onChange={mockOnChange} checked />);
    screen.getByRole("checkbox", { checked: true });

    fireEvent.click(screen.getByRole("checkbox"));
    expect(mockOnChange).toHaveBeenCalled();
  });
});
