import { fireEvent, render, screen } from "@testing-library/react";
import Flyover from "./Flyover";

const mockOnClose = jest.fn();

const children = <div>Content</div>;

describe(Flyover.name, () => {
  describe("when it renders", () => {
    beforeEach(() => {
      render(
        <Flyover title="Filters" onClose={mockOnClose} isOpen={true}>
          {children}
        </Flyover>
      );
    });

    it("should render the flyover", () => {
      screen.getByTestId("flyover");
    });

    it("should render the title", () => {
      screen.getByText(/filters/i);
    });

    it('should call the "onClose" callback', () => {
      const closeBtn = screen.getByRole("button");
      fireEvent.click(closeBtn);
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe("when it renders with the closed state", () => {
    it("shouldn't render the flyover", () => {
      render(
        <Flyover title="Filters" onClose={mockOnClose} isOpen={false}>
          {children}
        </Flyover>
      );
      const flyover = screen.queryByTestId("flyover");
      expect(flyover).not.toBeVisible();
    });
  });

  describe("when it renders with a footer", () => {
    it("should render the footer element", () => {
      render(
        <Flyover
          title="Filters"
          onClose={mockOnClose}
          isOpen={true}
          footer={<div>This is a footer</div>}
        >
          {children}
        </Flyover>
      );

      screen.getByRole("contentinfo");
      screen.getByText(/this is a footer/i);
    });
  });
});
