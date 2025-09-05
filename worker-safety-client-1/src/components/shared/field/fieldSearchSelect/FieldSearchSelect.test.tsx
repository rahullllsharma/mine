import type { InputSelectOption } from "../../inputSelect/InputSelect";
import { render } from "@testing-library/react";
import FieldSearchSelect from "./FieldSearchSelect";

const DUMMY_TASKS: InputSelectOption[] = [
  { id: "task_1", name: "Cable tray and support install" },
  { id: "task_2", name: "Clearing and grading" },
  { id: "task_3", name: "Control line installation" },
  { id: "task_4", name: "Excavation of soil using hydro-vac" },
  { id: "task_5", name: "Clearing" },
];

describe("FieldSearchSelect", () => {
  const selectHandler = jest.fn();

  it('should render with the "SearchSelect" component', () => {
    const { asFragment } = render(
      <FieldSearchSelect
        label="some label"
        options={DUMMY_TASKS}
        onSelect={selectHandler}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render a paragraph with the default option when the "readOnly" is set', () => {
    const { asFragment } = render(
      <FieldSearchSelect
        label="Lorem ipsum"
        options={DUMMY_TASKS}
        onSelect={selectHandler}
        defaultOption={DUMMY_TASKS[1]}
        readOnly
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
