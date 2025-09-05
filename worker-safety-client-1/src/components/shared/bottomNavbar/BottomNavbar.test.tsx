import { render } from "@testing-library/react";
import TabsMenuLight from "../tabs/menuLight/TabsMenuLight";
import BottomNavbar from "./BottomNavbar";

describe("BottomNavbar", () => {
  describe("when BottomNavbar renders", () => {
    it("should render correct items", () => {
      const navbarItems = [
        {
          name: "Projects",
          route: "/projects",
        },
        {
          name: "Map",
          route: "/map",
        },
        {
          name: "Menu",
          route: "/menu",
        },
      ];

      const { queryByTestId, getAllByRole } = render(
        <BottomNavbar
          content={
            <TabsMenuLight
              options={navbarItems}
              defaultIndex={0}
              onSelect={jest.fn()}
            />
          }
        />
      );

      expect(queryByTestId("bottom-navbar")).toBeTruthy();
      const tabs = getAllByRole("tab");
      expect(tabs[0].textContent).toEqual("Projects");
      expect(tabs[1].textContent).toEqual("Map");
      expect(tabs[2].textContent).toEqual("Menu");
    });
  });
});
