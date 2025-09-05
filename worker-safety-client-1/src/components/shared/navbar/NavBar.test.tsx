import { render } from "@testing-library/react";
import NavBar from "./NavBar";

describe("NavBar", () => {
  describe("when NavBar renders", () => {
    it("should render Urbint logo and title", () => {
      const navbarTitle = "Some text";
      const { queryByTestId, getByTitle } = render(
        <NavBar title="Some text" />
      );

      expect(queryByTestId("navbar")).toBeTruthy();
      expect(getByTitle("Urbint")).toBeTruthy();
      expect(queryByTestId("navbar-title")?.textContent).toEqual(navbarTitle);
    });
    it("should render right content if used", () => {
      const navbarRightContent = "Some text in right content";
      const { queryByTestId } = render(
        <NavBar title="Some text" rightContent={navbarRightContent} />
      );

      expect(queryByTestId("navbar-rightContent")?.textContent).toEqual(
        navbarRightContent
      );
    });
  });
});
