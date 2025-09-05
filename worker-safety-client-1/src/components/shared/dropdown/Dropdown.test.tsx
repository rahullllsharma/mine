import type { MenuItemProps } from "./Dropdown";
import { noop } from "lodash-es";
import { fireEvent, render, screen } from "@testing-library/react";
import ButtonPrimary from "../button/primary/ButtonPrimary";
import Dropdown from "./Dropdown";

const items: MenuItemProps[] = [
  { label: "opt1", onClick: noop, icon: "chevron_down" },
];

describe(Dropdown.name, () => {
  it("should render a button", () => {
    render(<Dropdown label="options" menuItems={[items]} />);
    screen.getByRole("button", { name: /options/i });
  });

  describe("when button is clicked", () => {
    beforeEach(() => {
      render(<Dropdown label="options" menuItems={[items]} />);

      const button = screen.getByRole("button", { name: /options/i });
      fireEvent.click(button);
    });

    it("should render a menu", () => {
      screen.getByRole("menu");
    });

    it(`should render ${items.length} menu items`, () => {
      const menuItems = screen.getAllByRole("menuitem");
      expect(menuItems).toHaveLength(items.length);
    });

    it("should render an item with icon", () => {
      expect(
        document
          .querySelector("[aria-hidden]")
          ?.classList.contains(`ci-chevron_down`)
      ).toBeTruthy();
    });
  });

  describe("when a right slot is provided in the menu items", () => {
    it("should render correctly", () => {
      const itemsWithRightSlot = [
        {
          ...items[0],
          rightSlot: <p>hello world</p>,
        },
      ];
      render(<Dropdown label="options" menuItems={[itemsWithRightSlot]} />);

      fireEvent.click(screen.getByRole("button", { name: /options/i }));

      expect(screen.getByText(/hello world/gi)).toBeInTheDocument();
    });
  });

  describe("when custom button is provided", () => {
    it("should render a custom button", () => {
      render(
        <Dropdown label="options" menuItems={[items]}>
          <ButtonPrimary label="customOptions"></ButtonPrimary>
        </Dropdown>
      );

      screen.getByRole("button", { name: /customOptions/i });
      expect(screen.queryByText("options")).not.toBeInTheDocument();
    });
  });
});
