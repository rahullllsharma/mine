import { render, screen } from "@testing-library/react";
import NavItem from "./NavItem";

describe(NavItem.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<NavItem name="Locations" />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when an icon is passed as a prop", () => {
    it("should contain an icon before the text", () => {
      const { asFragment } = render(
        <NavItem name="Locations" icon="location" />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when it renders as a "li"', () => {
    it("should render a list item instead of a div", () => {
      render(<NavItem name="Locations" icon="location" as="li" />);
      screen.getByRole("listitem");
    });
  });

  describe("when it's selected", () => {
    it("should render with a border", () => {
      render(<NavItem name="Locations" as="li" isSelected />);
      const navElement = screen.getByRole("listitem");
      expect(navElement.classList).toContain("border-neutral-shade-100");
    });
  });

  describe('when it\'s selected and the marker type is "left"', () => {
    it("should render with marker on the left side", () => {
      const { asFragment } = render(
        <NavItem name="Locations" markerType="left" isSelected />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when the status is "completed"', () => {
    it('should render with a "bg-brand-urbint-10" background', () => {
      render(<NavItem name="Locations" as="li" status="completed" />);
      const navElement = screen.getByRole("listitem");
      expect(navElement.classList).toContain("bg-brand-urbint-10");
    });

    it('should render with a "border-brand-urbint-30" border', () => {
      render(
        <NavItem name="Locations" as="li" isSelected status="completed" />
      );
      const navElement = screen.getByRole("listitem");
      expect(navElement.classList).toContain("border-brand-urbint-30");
    });
  });

  describe('when the status is "error"', () => {
    it('should render with a "bg-system-error-10" background', () => {
      render(<NavItem name="Locations" as="li" status="error" />);
      const navElement = screen.getByRole("listitem");
      expect(navElement.classList).toContain("bg-system-error-10");
    });

    it('should render with a "border-system-error-30" border', () => {
      render(<NavItem name="Locations" as="li" isSelected status="error" />);
      const navElement = screen.getByRole("listitem");
      expect(navElement.classList).toContain("border-system-error-30");
    });
  });
});
