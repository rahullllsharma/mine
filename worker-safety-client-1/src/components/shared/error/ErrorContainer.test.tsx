import { render, screen } from "@testing-library/react";
import ErrorContainer from "./ErrorContainer";

describe(ErrorContainer.name, () => {
  describe("when ErrorContainer renders", () => {
    it("should render a logo svg element ", () => {
      render(<ErrorContainer />);
      const logoElement = screen.getByAltText("Urbint");
      expect(logoElement).toBeInTheDocument();
    });

    it("should render a crash svg element ", () => {
      render(<ErrorContainer />);
      const errorImageElement = screen.getByAltText("ErrorImage");
      expect(errorImageElement).toBeInTheDocument();
    });

    it('should render a specific error message when the "notFoundError" prop is passed', () => {
      render(<ErrorContainer notFoundError />);
      screen.getByText("404: Page not found");
    });

    it("should display a button to redirect the user to the home screen when we are in the presence of a 404 error", () => {
      render(<ErrorContainer notFoundError />);
      screen.getByRole("button", { name: /go to home screen/i });
    });
  });
});
