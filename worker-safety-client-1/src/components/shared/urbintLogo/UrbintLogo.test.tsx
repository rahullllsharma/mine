import { render, screen } from "@testing-library/react";
import UrbintLogo from "./UrbintLogo";

describe("UrbintLogo", () => {
  describe("when UrbintLogo renders", () => {
    it("should render a svg element ", () => {
      render(<UrbintLogo />);
      const logoElement = screen.getByTitle("Urbint");
      expect(logoElement).toBeInTheDocument();
    });
  });
});
