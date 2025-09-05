import { render } from "@testing-library/react";
import PopoverIcon from "./PopoverIcon";

describe(PopoverIcon.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <PopoverIcon iconName="chevron_big_down" />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with tooltip props available", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <PopoverIcon
          iconName="chevron_big_down"
          tooltipProps={{ title: "Show me" }}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
