import type { InputSelectOption } from "../InputSelect";
import { fireEvent, render, screen } from "@testing-library/react";
import SearchSelect from "./SearchSelect";

const DUMMY_TASKS: InputSelectOption[] = [
  { id: "task_1", name: "Cable tray and support install" },
  { id: "task_2", name: "Clearing and grading" },
  { id: "task_3", name: "Control line installation" },
  { id: "task_4", name: "Excavation of soil using hydro-vac" },
  { id: "task_5", name: "Clearing" },
];

describe("SearchSelect", () => {
  const selectHandler = jest.fn();

  it("renders correctly", () => {
    const { asFragment } = render(
      <SearchSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders valid options when user enters a value in the search input", () => {
    render(
      <SearchSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
      />
    );
    const inputElement = screen.getByRole("combobox");
    const searchTerm = DUMMY_TASKS[4].name;

    fireEvent.change(inputElement, { target: { value: searchTerm } });

    const optionsDisplayed = screen.getAllByRole("option").length;
    const numberOfMatches = screen.getAllByRole("option", {
      name: new RegExp(searchTerm, "i"),
      exact: false,
    }).length;

    expect(optionsDisplayed).toEqual(numberOfMatches);
  });

  it("shouldn't render any options when the search term doesn't match any of the list items", () => {
    render(
      <SearchSelect
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        className="w-72"
        placeholder="select options"
      />
    );
    const inputElement = screen.getByRole("combobox");
    const searchTerm = "random searchTerm";

    fireEvent.change(inputElement, { target: { value: searchTerm } });

    expect(screen.queryAllByRole("option")).toHaveLength(0);
  });
});
