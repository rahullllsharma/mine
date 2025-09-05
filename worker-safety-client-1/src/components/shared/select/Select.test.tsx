import type { SelectOption, RenderOptionFn } from "./Select";
import { render, screen, fireEvent } from "@testing-library/react";
import Select from "./Select";

const DUMMY_LOCATIONS: SelectOption[] = [
  { id: 1, name: "Location 1" },
  { id: 2, name: "Location 2" },
  { id: 3, name: "Location 3" },
  { id: 4, name: "Location 4" },
];

const itemSelectHandler = jest.fn();

describe("Select", () => {
  const renderOptionFn: RenderOptionFn = ({ option: { name } }) => (
    <li>{name}</li>
  );
  it("renders", () => {
    const { asFragment } = render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );

    expect(asFragment()).toMatchSnapshot();

    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toBeInTheDocument();
  });

  it("should be disabled if no options are available", () => {
    render(
      <Select
        options={[]}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );
    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toBeDisabled();
  });

  it('should render the default option if "defaultOption" is provided and is valid', () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        defaultOption={DUMMY_LOCATIONS[1]}
        renderOptionFn={renderOptionFn}
      />
    );
    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toHaveTextContent(DUMMY_LOCATIONS[1].name);
  });

  it("should display a list of options when the select is clicked", async () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );
    fireEvent.click(screen.getByRole("button"));

    const listElement = screen.getByRole("listbox");
    expect(listElement).toBeInTheDocument();
  });

  it('should display a list of elements that match the length of the "options" array', async () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );
    fireEvent.click(screen.getByRole("button"));

    const listItems = screen.getAllByRole("option");
    expect(listItems.map(option => option.textContent).join("")).toEqual(
      DUMMY_LOCATIONS.map(option => option.name).join("")
    );
  });

  it("should update the select option when a list item is clicked", () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    fireEvent.click(screen.getByText(DUMMY_LOCATIONS[2].name));

    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toHaveTextContent(DUMMY_LOCATIONS[2].name);
  });

  it('should call the "onSelect" callback when "onChange" event is triggered', () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    fireEvent.click(screen.getByText(DUMMY_LOCATIONS[2].name));
    expect(itemSelectHandler).toHaveBeenCalledWith(DUMMY_LOCATIONS[2]);
  });

  it('should render a small button if "size" prop is set to "small', () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
        size="small"
      />
    );
    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toHaveClass("h-7");
  });

  it('should render a button with a custom placeholder when "placeholder" is provided', () => {
    render(
      <Select
        options={DUMMY_LOCATIONS}
        onSelect={itemSelectHandler}
        renderOptionFn={renderOptionFn}
        placeholder="Select a control"
      />
    );
    const buttonElement = screen.getByRole("button", {
      name: /select a control/i,
    });
    expect(buttonElement).toBeInTheDocument();
  });
});
