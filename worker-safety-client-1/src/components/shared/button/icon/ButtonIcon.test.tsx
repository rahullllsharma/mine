import { fireEvent, render, screen } from "@testing-library/react";
import ButtonIcon from "./ButtonIcon";

describe("ButtonIcon", () => {
  describe("when is rendered", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<ButtonIcon iconName="settings_filled" />);
      expect(asFragment()).toMatchSnapshot();
    });

    it("should be in the document", () => {
      render(<ButtonIcon iconName="settings_filled" />);
      expect(screen.getByRole("button")).toBeInTheDocument();
    });
  });

  describe("when is loading", () => {
    it("should be disabled and showing the loading icon", () => {
      const { asFragment } = render(
        <ButtonIcon loading iconName="settings_filled" />
      );
      expect(screen.getByRole("button")).toBeDisabled();
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when is disabled", () => {
    it('should have the "disabled" attribute', () => {
      render(<ButtonIcon iconName="settings_filled" disabled />);
      expect(screen.getByRole("button")).toBeDisabled();
    });
  });

  describe("when is clicked", () => {
    const mockOnClick = jest.fn();

    it('should have the "onClick" callback to be called', () => {
      render(<ButtonIcon iconName="settings_filled" onClick={mockOnClick} />);
      fireEvent.click(screen.getByRole("button"));
      expect(mockOnClick).toBeCalled();
    });
  });
});
