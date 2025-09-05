import { fireEvent, render, screen, within } from "@testing-library/react";
import * as deviceDetect from "react-device-detect";
import { mockTenantStore } from "@/utils/dev/jest";
import NavBarWorkerSafety from "./NavBarWorkerSafety";

jest.mock("next/router", () => ({
  __esModule: true,
  default: jest.fn(),
  useRouter: jest.fn(() => ({
    pathname: "pathname",
    push: jest.fn(),
  })),
}));

describe(NavBarWorkerSafety.name, () => {
  mockTenantStore();

  it("should render a Tabs menu", () => {
    render(<NavBarWorkerSafety />);
    screen.getByRole("tablist");
  });

  describe("Desktop version", () => {
    beforeEach(() => {
      Object.defineProperty(deviceDetect, "isDesktop", { get: () => true });
      Object.defineProperty(deviceDetect, "isTablet", { get: () => false });
      Object.defineProperty(deviceDetect, "isMobile", { get: () => false });
      render(<NavBarWorkerSafety />);
    });

    it("should render an avatar in the right section", () => {
      expect(
        within(screen.getByTestId("navbar-rightContent")).getByRole("img")
      ).toBeInTheDocument();
    });

    it("should render a menu when button in the right section is clicked", () => {
      const button = within(
        screen.getByTestId("navbar-rightContent")
      ).getByRole("button");
      fireEvent.click(button);

      expect(screen.getByRole("menu")).toBeInTheDocument();
    });
  });

  describe("Tablet and/or mobile version", () => {
    beforeEach(() => {
      Object.defineProperty(deviceDetect, "isDesktop", { get: () => false });
      Object.defineProperty(deviceDetect, "isTablet", { get: () => true });
      Object.defineProperty(deviceDetect, "isMobile", { get: () => true });
      render(<NavBarWorkerSafety />);
    });

    it("should not render right section", () => {
      const navbarRightContent = screen.queryByTestId("navbar-rightContent");
      expect(navbarRightContent).toBeNull();
    });
  });
});
