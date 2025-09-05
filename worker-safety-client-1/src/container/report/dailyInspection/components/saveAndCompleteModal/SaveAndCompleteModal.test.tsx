import { screen, render, fireEvent } from "@testing-library/react";
import SaveAndCompleteModal from "./SaveAndCompleteModal";

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe(SaveAndCompleteModal.name, () => {
  it("should render the modal correctly", () => {
    render(
      <SaveAndCompleteModal
        isOpen
        closeModal={jest.fn}
        onPrimaryBtnClick={jest.fn}
      />
    );

    screen.getByText(/are you sure you want to complete this report/i);
    screen.getByText(
      /you will not be able to make changes once you\'ve completed the report/i
    );

    screen.getByRole("button", { name: /save and finish later/i });
    screen.getByRole("button", { name: /complete report/i });
  });

  describe("when the modal is in a loading state (the parent is making an async operation)", () => {
    it("should disable all buttons", () => {
      render(
        <SaveAndCompleteModal
          isOpen
          isLoading
          closeModal={jest.fn}
          onPrimaryBtnClick={jest.fn}
        />
      );

      expect(
        screen.getByRole("button", { name: /save and finish later/i })
      ).toBeDisabled();

      expect(screen.getByRole("button", { name: /saving/i })).toBeDisabled();
    });
  });

  it("should call the `closeModal` callback when clicking save and finish later", () => {
    const mockCloseModal = jest.fn();
    render(
      <SaveAndCompleteModal
        isOpen
        closeModal={mockCloseModal}
        onPrimaryBtnClick={jest.fn}
      />
    );

    fireEvent.click(
      screen.getByRole("button", { name: /save and finish later/i })
    );

    expect(mockCloseModal).toHaveBeenCalled();
  });

  it("should call the `onPrimaryBtnClick` callback when clicking save and finish later", () => {
    const mockOnPrimaryBtnClick = jest.fn();
    render(
      <SaveAndCompleteModal
        isOpen
        closeModal={jest.fn}
        onPrimaryBtnClick={mockOnPrimaryBtnClick}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /complete report/i }));

    expect(mockOnPrimaryBtnClick).toHaveBeenCalled();
  });
});
