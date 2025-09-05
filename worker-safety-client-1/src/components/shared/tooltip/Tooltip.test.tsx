import {
  fireEvent,
  render,
  screen,
  waitForElementToBeRemoved,
} from "@testing-library/react";
import Tooltip from "./Tooltip";

describe(Tooltip.name, () => {
  describe("when it renders", () => {
    it("should render a paragraph to trigger a tooltip", () => {
      render(
        <Tooltip title="This is a tooltip">
          <p>Hover me</p>
        </Tooltip>
      );
      screen.getByText(/hover me/i);
    });
  });

  describe("when we mouse over the paragraph", () => {
    it("should display a tooltip on top", () => {
      render(
        <Tooltip title="This is a tooltip">
          <p>Hover me</p>
        </Tooltip>
      );
      fireEvent.mouseOver(screen.getByText(/hover me/i));
      const tooltipElement = screen.getByText(/this is a tooltip/i);
      expect(tooltipElement).toHaveAttribute("data-position", "top");
    });

    it("should display a tooltip on bottom", () => {
      render(
        <Tooltip title="This is a tooltip" position="bottom">
          <p>Hover me</p>
        </Tooltip>
      );
      fireEvent.mouseOver(screen.getByText(/hover me/i));
      const tooltipElement = screen.getByText(/this is a tooltip/i);
      expect(tooltipElement).toHaveAttribute("data-position", "bottom");
    });

    it("should display a tooltip on the left", () => {
      render(
        <Tooltip title="This is a tooltip" position="left">
          <p>Hover me</p>
        </Tooltip>
      );
      fireEvent.mouseOver(screen.getByText(/hover me/i));
      const tooltipElement = screen.getByText(/this is a tooltip/i);
      expect(tooltipElement).toHaveAttribute("data-position", "left");
    });

    it("should display a tooltip on the right", () => {
      render(
        <Tooltip title="This is a tooltip" position="right">
          <p>Hover me</p>
        </Tooltip>
      );
      fireEvent.mouseOver(screen.getByText(/hover me/i));
      const tooltipElement = screen.getByText(/this is a tooltip/i);
      expect(tooltipElement).toHaveAttribute("data-position", "right");
    });

    it('shouldn\'t display a tooltip if the "isDisabled" prop is passed', () => {
      render(
        <Tooltip title="This is a tooltip" isDisabled>
          <p>Hover me</p>
        </Tooltip>
      );
      fireEvent.mouseOver(screen.getByText(/hover me/i));
      const tooltipElement = screen.queryByText(/this is a tooltip/i);
      expect(tooltipElement).toBeNull();
    });
  });

  describe("when we mouse leave the paragraph", () => {
    it("should hide the tooltip", async () => {
      render(
        <Tooltip title="This is a tooltip">
          <p>Hover me</p>
        </Tooltip>
      );
      const triggerElement = screen.getByText(/hover me/i);
      fireEvent.mouseOver(triggerElement);
      screen.getByText(/this is a tooltip/i);
      fireEvent.mouseLeave(triggerElement);
      const tooltipElement = screen.getByText(/this is a tooltip/i);
      await waitForElementToBeRemoved(tooltipElement);
      expect(tooltipElement).not.toBeInTheDocument();
    });
  });
});
