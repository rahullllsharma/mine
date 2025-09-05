import { render, screen, fireEvent } from "@testing-library/react";
import { openSelectMenu } from "@/utils/dev/jest";
import SelectCard from "./SelectCard";

const CONTROL_LIBRARY = [
  { id: "1", name: "Control 1" },
  { id: "2", name: "Control 2" },
  { id: "3", name: "Control 3" },
];

const mockOnSelect = jest.fn();
const mockOnRemove = jest.fn();

describe(SelectCard.name, () => {
  it("should render a select, an avatar and a empty trash icon", () => {
    const { asFragment } = render(
      <SelectCard
        options={CONTROL_LIBRARY}
        userInitials="UB"
        type="control"
        onSelect={mockOnSelect}
        onRemove={mockOnRemove}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should call the "mockOnSelect" callback when "onSelect" event is triggered', () => {
    render(
      <SelectCard
        options={CONTROL_LIBRARY}
        userInitials="UB"
        type="control"
        placeholder="Select a control"
        onSelect={mockOnSelect}
        onRemove={mockOnRemove}
      />
    );

    openSelectMenu("button", /select a control/i);

    fireEvent.click(screen.getByText(CONTROL_LIBRARY[2].name));
    expect(mockOnSelect).toHaveBeenCalledWith({
      id: CONTROL_LIBRARY[2].id,
      name: CONTROL_LIBRARY[2].name,
    });
  });

  it('should call the "mockOnRemove" callback when "onRemove" event is triggered', () => {
    render(
      <SelectCard
        options={CONTROL_LIBRARY}
        userInitials="UB"
        type="control"
        onSelect={mockOnSelect}
        onRemove={mockOnRemove}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /remove/i }));
    expect(mockOnRemove).toHaveBeenCalled();
  });

  it('should render with a border if prop "type" is defined as "control"', () => {
    render(
      <SelectCard
        options={CONTROL_LIBRARY}
        userInitials="UB"
        type="control"
        onSelect={mockOnSelect}
        onRemove={mockOnRemove}
      />
    );
    const containerElement = screen.getByTestId("ControlSelectCard");
    expect(containerElement).toHaveClass(
      "border border-dashed border-brand-gray-30 rounded"
    );
  });

  it('should render without border styles if prop "type" is defined as "hazard"', () => {
    render(
      <SelectCard
        options={CONTROL_LIBRARY}
        userInitials="UB"
        type="hazard"
        onSelect={mockOnSelect}
        onRemove={mockOnRemove}
      />
    );
    const containerElement = screen.getByTestId("ControlSelectCard");
    expect(containerElement).not.toHaveClass(
      "border border-dashed border-brand-gray-30 rounded"
    );
  });

  describe("when is disabled", () => {
    it("should render without a select", () => {
      render(
        <SelectCard
          options={CONTROL_LIBRARY}
          userInitials="UB"
          type="hazard"
          isDisabled
          onSelect={mockOnSelect}
          onRemove={mockOnRemove}
        />
      );
      const selectElement = screen.queryByRole("button", {
        name: /select a control/i,
      });
      expect(selectElement).toBeNull();
    });

    it("should render with a paragraph with the default option", () => {
      render(
        <SelectCard
          options={CONTROL_LIBRARY}
          userInitials="UB"
          type="hazard"
          defaultOption={CONTROL_LIBRARY[1]}
          isDisabled
          onSelect={mockOnSelect}
          onRemove={mockOnRemove}
        />
      );
      const paragraphElement = screen.getByText(
        new RegExp(CONTROL_LIBRARY[1].name, "i")
      );
      expect(paragraphElement).toBeInTheDocument();
    });
  });
});
