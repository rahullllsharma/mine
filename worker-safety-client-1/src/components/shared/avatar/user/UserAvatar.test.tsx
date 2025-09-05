import { fireEvent, render, screen } from "@testing-library/react";
import UserAvatar from "./UserAvatar";

describe("UserAvatar", () => {
  it('should render with the "UserAvatar" component', () => {
    const { asFragment } = render(<UserAvatar name="UB" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should initially not render hover component", () => {
    render(
      <UserAvatar
        hoverElement={<p data-testid="hover-test-element">Hello there</p>}
        name="UB"
      />
    );

    const hoverTestElement = screen.queryByTestId("hover-test-element");
    expect(hoverTestElement).toBeNull();
  });

  it("should render hover component on mouse enter", () => {
    render(
      <UserAvatar
        hoverElement={<p data-testid="hover-test-element">I am a user!</p>}
        name="UB"
      />
    );

    const userAvatarIcon = screen.getByTestId("user-avatar-icon");

    fireEvent.mouseEnter(userAvatarIcon);
    const hoverTestElement = screen.queryByTestId("hover-test-element");
    expect(hoverTestElement).toBeTruthy();
    expect(hoverTestElement?.textContent).toEqual("I am a user!");
  });
});
