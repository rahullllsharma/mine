import { fireEvent, render, screen } from "@testing-library/react";
import Popover from "./Popover";

const trigger = (): JSX.Element => <button>Open me</button>;

describe(Popover.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<Popover triggerComponent={trigger} />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when the popover is opened", () => {
    it("should open the popover content", () => {
      const { asFragment } = render(
        <Popover triggerComponent={trigger}>
          <div>Content</div>
        </Popover>
      );
      fireEvent.click(screen.getByRole("button"));
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
