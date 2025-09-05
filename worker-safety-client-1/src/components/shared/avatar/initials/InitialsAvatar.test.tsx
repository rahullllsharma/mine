import { render, screen } from "@testing-library/react";
import InitialsAvatar from "./InitialsAvatar";

describe("Avatar", () => {
  it('should render with the "InitialsAvatar" component', () => {
    const { asFragment } = render(<InitialsAvatar name="UB" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render with the first two chars from the "initials" prop if the value has more than two chars', () => {
    render(<InitialsAvatar name="URBINT" />);
    const textElement = screen.getByText("UR");
    expect(textElement).toBeInTheDocument();
  });

  it('should render with the first two chars from the "initials" prop if the value has whitespaces ', () => {
    render(<InitialsAvatar name="U RBINT" />);
    const textElement = screen.getByText("UR");
    expect(textElement).toBeInTheDocument();
  });
});
