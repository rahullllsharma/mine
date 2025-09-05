import { render } from "@testing-library/react";
import PopoverPrimary from "./PopoverPrimary";

describe(PopoverPrimary.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<PopoverPrimary label="Open me" />);
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
