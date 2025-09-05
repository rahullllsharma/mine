import { render } from "@testing-library/react";
import Paragraph from "./Paragraph";

describe(Paragraph.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<Paragraph text="Lorem ipsum" />);
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
