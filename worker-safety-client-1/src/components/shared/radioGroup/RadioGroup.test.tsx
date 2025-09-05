import type { RadioGroupOption } from "./RadioGroup";
import { render, screen, fireEvent } from "@testing-library/react";
import RadioGroup from "./RadioGroup";

const DUMMY_OPTIONS: RadioGroupOption[] = [
  { id: 1, value: "Option 1" },
  { id: 2, value: "Option 2" },
  { id: 3, value: "Option 3" },
  { id: 4, value: "Option 4" },
];

const onSelectHandler = jest.fn();

describe("RadioGroup", () => {
  it("should render", () => {
    render(<RadioGroup options={DUMMY_OPTIONS} onSelect={onSelectHandler} />);
    const radioGroupElement = screen.getByRole("radiogroup");
    expect(radioGroupElement).toBeInTheDocument();
  });

  it('shouldn\'t have options if the "options" property is an empty array', () => {
    render(<RadioGroup options={[]} onSelect={onSelectHandler} />);
    const radioElements = screen.queryAllByRole("radio");
    expect(radioElements).toHaveLength(0);
  });

  it('should have as many options as the ones provided by the "options" array', () => {
    render(<RadioGroup options={DUMMY_OPTIONS} onSelect={onSelectHandler} />);
    const radioElements = screen.getAllByRole("radio");
    expect(radioElements).toHaveLength(DUMMY_OPTIONS.length);
  });

  it("shouldn't have any option selected when rendered", () => {
    render(<RadioGroup options={DUMMY_OPTIONS} onSelect={onSelectHandler} />);
    const radioElements = screen.queryAllByRole("radio", { checked: true });
    expect(radioElements).toHaveLength(0);
  });

  it('should have default option checked if the "isDefault" property is set to true', () => {
    render(
      <RadioGroup
        options={DUMMY_OPTIONS}
        defaultOption={{ id: 1, value: "Option 1" }}
        onSelect={onSelectHandler}
      />
    );
    const radioElements = screen.getAllByRole("radio");
    expect(radioElements[0]).toBeChecked();
  });

  it("should select an option when clicked", () => {
    render(<RadioGroup options={DUMMY_OPTIONS} onSelect={onSelectHandler} />);
    const radioElements = screen.getAllByRole("radio");
    fireEvent.click(radioElements[0]);
    expect(radioElements[0]).toBeChecked();
  });

  it("shouldn't allow to be checked/unchecked if option is disabled", () => {
    render(
      <RadioGroup
        options={DUMMY_OPTIONS}
        isDisabled={true}
        onSelect={onSelectHandler}
      />
    );
    const radioElements = screen.getAllByRole("radio");
    fireEvent.click(radioElements[1]);
    expect(radioElements[1]).not.toBeChecked();
  });

  it('shouldn\'t show options with text if "hideLabels" prop is set to true', () => {
    render(
      <RadioGroup
        options={DUMMY_OPTIONS}
        hideLabels={true}
        onSelect={onSelectHandler}
      />
    );
    const radioElements = screen.getAllByRole("radio");
    expect(radioElements.map(element => element.textContent).join("")).toEqual(
      ""
    );
  });

  it("should call the onSelect callback when onChange is triggered", () => {
    render(<RadioGroup options={DUMMY_OPTIONS} onSelect={onSelectHandler} />);
    const radioElements = screen.getAllByRole("radio");
    fireEvent.click(radioElements[1]);
    expect(onSelectHandler).toHaveBeenCalledWith(DUMMY_OPTIONS[1].value);
  });
});
