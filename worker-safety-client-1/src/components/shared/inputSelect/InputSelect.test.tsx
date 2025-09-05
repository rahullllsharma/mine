import type { InputSelectOption } from "./InputSelect";
import { fireEvent, render, screen } from "@testing-library/react";
import { formRender, openSelectMenu } from "@/utils/dev/jest";
import InputSelect from "./InputSelect";

const DUMMY_TASKS: InputSelectOption[] = [
  { id: "task_1", name: "Cable tray and support install" },
  { id: "task_2", name: "Clearing and grading" },
  { id: "task_3", name: "Control line installation" },
  { id: "task_4", name: "Excavation of soil using hydro-vac" },
  {
    id: "task_5",
    name: "Excavation of soil (using means other than hydro-vac)",
  },
];

describe("InputSelect", () => {
  const selectHandler = jest.fn();

  it("renders correctly", () => {
    const { asFragment } = formRender(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
        isSearchable
      />
    );

    expect(asFragment()).toMatchSnapshot();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should render the task list when clicked", () => {
    const { asFragment } = render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
        isSearchable
      />
    );

    openSelectMenu();
    expect(asFragment()).toMatchSnapshot();
  });

  it("should be disabled if no options are available", () => {
    render(
      <InputSelect
        options={[]}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
      />
    );
    expect(screen.getByRole("combobox")).toBeDisabled();
  });

  it('should render the default option if "defaultOption" is provided and valid', () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        defaultOption={DUMMY_TASKS[2]}
        isSearchable
      />
    );

    expect(screen.getByRole("button")).toHaveTextContent(DUMMY_TASKS[2].name);
  });

  it("should update the selected option when an item is clicked", () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
        isSearchable
      />
    );
    openSelectMenu();
    fireEvent.click(screen.getByText(DUMMY_TASKS[3].name));

    expect(screen.getByRole("button")).toHaveTextContent(DUMMY_TASKS[3].name);
  });

  it('should call the "onSelect" callback when "onChange" event is triggered', () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
        isSearchable
      />
    );
    openSelectMenu();

    fireEvent.click(screen.getByText(DUMMY_TASKS[3].name));
    expect(selectHandler).toHaveBeenCalled();
  });

  it('should render a button with a custom placeholder when "placeholder" is provided', () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="custom placeholder"
        isSearchable
      />
    );
    const selectElement = screen.getByRole("button", {
      name: /custom placeholder/i,
    });
    expect(selectElement).toBeInTheDocument();
  });

  it("should render a red border indicating that the select is in an invalid state", () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select option"
        isInvalid
        isSearchable
      />
    );
    const selectElement = screen.getByRole("button");
    expect(selectElement).toHaveClass(
      "border-system-error-40 focus-within:ring-system-error-40"
    );
  });

  it('should display a list with the same amount of items as the "options" array length', () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select option"
        isSearchable
      />
    );
    openSelectMenu();

    const listItems = screen.getAllByRole("option");
    expect(listItems.map(option => option.textContent).join("")).toEqual(
      DUMMY_TASKS.map(option => option.name).join("")
    );
  });

  it('should display the message "No options available" when the search does not return results', () => {
    render(
      <InputSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select option"
        isSearchable
      />
    );
    openSelectMenu();
    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "some searchTerm" },
    });
    screen.getByText("No options available");
  });

  describe("when icon is passed", () => {
    it("should render an icon in the select container", () => {
      const icon = "user";
      render(
        <InputSelect
          options={DUMMY_TASKS}
          onSelect={selectHandler}
          className="w-72"
          placeholder="select options"
          isSearchable
          icon="user"
        />
      );
      expect(
        document
          .querySelector("[aria-hidden]")
          ?.classList.contains(`ci-${icon}`)
      ).toBeTruthy();
    });
  });
});
