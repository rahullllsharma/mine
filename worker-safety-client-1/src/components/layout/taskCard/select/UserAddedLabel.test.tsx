import { render } from "@testing-library/react";
import UserAddedLabel from "./UserAddedLabel";

describe("UserAvatar", () => {
  it('should render with the "UserAvatar" component', async () => {
    const { asFragment } = render(
      <UserAddedLabel label="User added control" />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
