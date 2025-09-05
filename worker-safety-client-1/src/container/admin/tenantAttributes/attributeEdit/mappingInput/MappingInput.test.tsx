import { render, screen, fireEvent } from "@testing-library/react";
import { MappingInput } from "./MappingInput";

describe(MappingInput.name, () => {
  const mockOnSubmit = jest.fn();

  describe("when rendering without extra text", () => {
    it("should show the label and the extra text", () => {
      render(
        <MappingInput
          badgeNumber={1}
          label="Label"
          defaultLabel="Default"
          onSubmit={mockOnSubmit}
        />
      );

      screen.getByText("Label");
    });
  });

  describe("when rendering with extra text", () => {
    it("should show only the label", () => {
      render(
        <MappingInput
          badgeNumber={1}
          label="Label"
          defaultLabel="Default"
          isDefault
          onSubmit={mockOnSubmit}
        />
      );

      screen.getByText("Label (default)");
    });
  });

  describe("when clicking the edit button", () => {
    it("should transform the element into an input", () => {
      render(
        <MappingInput
          badgeNumber={1}
          label="Label"
          defaultLabel="Default"
          isDefault
          onSubmit={mockOnSubmit}
        />
      );

      const buttonElement = screen.getByRole("button");
      fireEvent.click(buttonElement);

      screen.getByDisplayValue("Label");
    });

    describe("when the input is visible", () => {
      beforeEach(() => {
        render(
          <MappingInput
            badgeNumber={1}
            label="Label"
            defaultLabel="Default"
            isDefault
            onSubmit={mockOnSubmit}
          />
        );

        const buttonElement = screen.getByRole("button");
        fireEvent.click(buttonElement);
      });

      it("should update the list element after submit", () => {
        const inputElement = screen.getByDisplayValue("Label");
        fireEvent.change(inputElement, { target: { value: "New label" } });

        // submit button
        const buttonElement = screen.getAllByRole("button")[0];
        fireEvent.click(buttonElement);

        screen.getByText("Label (default)");
      });

      it("should revert to label after canceling", () => {
        const inputElement = screen.getByDisplayValue("Label");
        fireEvent.change(inputElement, { target: { value: "New label" } });

        // clear button
        const buttonElement = screen.getAllByRole("button")[1];
        fireEvent.click(buttonElement);

        screen.getByText("Label (default)");
      });
    });
  });

  describe("when the label is different from the default", () => {
    it("should display the tooltip", async () => {
      render(
        <MappingInput
          badgeNumber={1}
          label="Label"
          defaultLabel="Default"
          isDefault
          onSubmit={mockOnSubmit}
        />
      );

      const tooltipElement = screen.getByLabelText("mapping-tooltip");
      fireEvent.mouseOver(tooltipElement);
      await screen.findByText(/Original value: "Default"/);
    });
  });
});
