import { render, screen, fireEvent } from "@testing-library/react";
import Toast from "./Toast";

const mockOnDismiss = jest.fn();

describe(Toast.name, () => {
  describe("when it renders without a type", () => {
    it("shouldn't render without an icon", () => {
      const { asFragment } = render(
        <Toast message="Lorem Ipsum" onDismiss={mockOnDismiss} />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with a type", () => {
    it('should render an error icon when type is "error"', () => {
      const { asFragment } = render(
        <Toast message="Lorem Ipsum" type="error" onDismiss={mockOnDismiss} />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it('should render an warning icon when type is "warning"', () => {
      const { asFragment } = render(
        <Toast message="Lorem Ipsum" type="warning" onDismiss={mockOnDismiss} />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it('should render an info icon when type is "info"', () => {
      const { asFragment } = render(
        <Toast message="Lorem Ipsum" type="info" onDismiss={mockOnDismiss} />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it('should render an warning success when type is "success"', () => {
      const { asFragment } = render(
        <Toast message="Lorem Ipsum" type="success" onDismiss={mockOnDismiss} />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when "onDismiss" is pressed', () => {
    it("should trigger the callback", () => {
      render(<Toast message="Lorem Ipsum" onDismiss={mockOnDismiss} />);
      fireEvent.click(screen.getByRole("button"));
      expect(mockOnDismiss).toHaveBeenCalled();
    });
  });
});
