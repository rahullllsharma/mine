import { fireEvent, render, screen } from "@testing-library/react";
import Modal from "./Modal";

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe("Modal", () => {
  describe("when is open", () => {
    const mockCloseModal = jest.fn();
    const title = "Lorem ipsum";

    it("should render a title", () => {
      render(<Modal title={title} isOpen={true} closeModal={mockCloseModal} />);
      const headingElement = screen.getByRole("heading", { name: title });
      expect(headingElement).toBeInTheDocument();
    });

    it("should render a description", () => {
      const description =
        "Vestibulum dictum viverra condimentum. Suspendisse cursus, sapien quis dapibus dictum, augue libero blandit magna, eget lacinia ante quam in metus.";
      render(
        <Modal title={title} isOpen={true} closeModal={mockCloseModal}>
          {description}
        </Modal>
      );
      const descriptionElement = screen.getByText(description);
      expect(descriptionElement).toBeInTheDocument();
    });

    describe("when close button is clicked", () => {
      it("should call 'closeModel()'", () => {
        render(
          <Modal title={title} isOpen={true} closeModal={mockCloseModal} />
        );

        const closeButtonElement = screen.getByRole("button", {
          name: /close modal/i,
        });
        fireEvent.click(closeButtonElement);
        expect(mockCloseModal).toHaveBeenCalled();
      });
    });
  });

  describe("when is closed", () => {
    const mockCloseModal = jest.fn();
    const title = "Lorem ipsum";

    it("should not be in the document", () => {
      render(
        <Modal title={title} isOpen={false} closeModal={mockCloseModal} />
      );
      const headingElement = screen.queryByRole("heading", { name: title });
      expect(headingElement).not.toBeInTheDocument();
    });
  });
});
