import type { InputSelectOption } from "../InputSelect";
import { fireEvent, render, screen } from "@testing-library/react";
import { openSelectMenu } from "@/utils/dev/jest";
import MultiSelect from "./MultiSelect";

const DUMMY_OPTIONS: InputSelectOption[] = [
  { id: "m_1", name: "César Teixeira" },
  { id: "m_2", name: "João Centeno" },
  { id: "m_3", name: "João Lemos" },
  { id: "m_4", name: "José Silva" },
  { id: "m_5", name: "Paulo Sousa" },
];

describe(MultiSelect.name, () => {
  const selectHandler = jest.fn();

  it("should render correctly", () => {
    const { asFragment } = render(
      <MultiSelect
        options={DUMMY_OPTIONS}
        onSelect={selectHandler}
        placeholder="select options"
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should add option chips to the control container when selected from the options list", () => {
    render(
      <MultiSelect
        options={DUMMY_OPTIONS}
        onSelect={selectHandler}
        placeholder="select options"
      />
    );
    openSelectMenu();
    fireEvent.click(
      screen.getByRole("option", { name: DUMMY_OPTIONS[1].name })
    );
    openSelectMenu();
    fireEvent.click(
      screen.getByRole("option", { name: DUMMY_OPTIONS[2].name })
    );
    screen.getByText(DUMMY_OPTIONS[1].name);
    screen.getByText(DUMMY_OPTIONS[2].name);
  });

  it('should remove an option chip from the control container when clicking the "close" button', () => {
    render(
      <MultiSelect
        options={DUMMY_OPTIONS}
        onSelect={selectHandler}
        placeholder="select options"
      />
    );
    openSelectMenu();
    fireEvent.click(
      screen.getByRole("option", { name: DUMMY_OPTIONS[1].name })
    );
    screen.getByText(DUMMY_OPTIONS[1].name);
    fireEvent.click(screen.getByLabelText(`Remove ${DUMMY_OPTIONS[1].name}`));

    expect(screen.queryByText(DUMMY_OPTIONS[1].name)).toBeNull();
  });

  it("should render correctly the default options if they are provided and valid", () => {
    render(
      <MultiSelect
        options={DUMMY_OPTIONS}
        onSelect={selectHandler}
        defaultOption={[DUMMY_OPTIONS[1], DUMMY_OPTIONS[2]]}
      />
    );
    screen.getByText(DUMMY_OPTIONS[1].name);
    screen.getByText(DUMMY_OPTIONS[2].name);
  });
});
