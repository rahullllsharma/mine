import type { InputSelectOption } from "../../inputSelect/InputSelect";
import { render, screen } from "@testing-library/react";
import FieldMultiSelect from "./FieldMultiSelect";

const DUMMY_OPTIONS: InputSelectOption[] = [
  { id: "m_1", name: "César Teixeira" },
  { id: "m_2", name: "João Centeno" },
  { id: "m_3", name: "João Lemos" },
  { id: "m_4", name: "José Silva" },
  { id: "m_5", name: "Paulo Sousa" },
];

describe("FieldMultiSelect", () => {
  const selectHandler = jest.fn();

  it('should render with the "MultiSelect" component', () => {
    const { asFragment } = render(
      <FieldMultiSelect
        label="Project managers"
        options={DUMMY_OPTIONS}
        onSelect={selectHandler}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render a paragraph with the default options when the "readOnly" is set', () => {
    render(
      <FieldMultiSelect
        label="Project managers"
        options={DUMMY_OPTIONS}
        defaultOption={[DUMMY_OPTIONS[1], DUMMY_OPTIONS[2]]}
        readOnly
        onSelect={selectHandler}
      />
    );
    screen.getByText(`${DUMMY_OPTIONS[1].name}, ${DUMMY_OPTIONS[2].name}`);
  });

  it('should render an empty paragraph if no default options is given when the "readOnly" is set', () => {
    const { asFragment } = render(
      <FieldMultiSelect
        label="Project managers"
        options={DUMMY_OPTIONS}
        readOnly
        onSelect={selectHandler}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
