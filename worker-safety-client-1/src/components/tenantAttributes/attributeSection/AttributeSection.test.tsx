import { render, screen, fireEvent } from "@testing-library/react";
import { AttributeSection } from "./AttributeSection";

describe(AttributeSection.name, () => {
  const mockOnClick = jest.fn();

  it("should render with label", () => {
    render(
      <AttributeSection
        label="Label"
        defaultLabel="Label"
        onEditClick={mockOnClick}
      />
    );

    screen.getByText("Label");
  });

  it("should trigger button callback", () => {
    render(
      <AttributeSection
        label="Label"
        defaultLabel="Label"
        onEditClick={mockOnClick}
      />
    );

    const buttonElement = screen.getByRole("button");

    fireEvent.click(buttonElement);
    expect(mockOnClick).toHaveBeenCalled();
  });

  it("should render with children", () => {
    render(
      <AttributeSection
        label="Label"
        defaultLabel="Label"
        onEditClick={mockOnClick}
      >
        <div>Children Content</div>
      </AttributeSection>
    );

    screen.getByText("Children Content");
  });

  describe("when having a non default label", () => {
    it("should display the tooltip", async () => {
      render(
        <AttributeSection
          label="Label"
          defaultLabel="Default label"
          onEditClick={mockOnClick}
        />
      );

      const tooltipElement = screen.getByLabelText("attribute-tooltip");
      fireEvent.mouseOver(tooltipElement);
      await screen.findByText(/Original value: "Default label"/);
    });
  });
});
