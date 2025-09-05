import type { FieldRadioGroupProps } from "./FieldRadioGroup";
import { render } from "@testing-library/react";
import FieldRadioGroup from "./FieldRadioGroup";

const DUMMY_OPTIONS: FieldRadioGroupProps["options"] = [
  { id: 1, value: "One" },
  { id: 2, value: "Two" },
  { id: 3, value: "Three" },
];

describe(FieldRadioGroup.name, () => {
  it('should render with the "RadioGroup" component', () => {
    const { asFragment } = render(
      <FieldRadioGroup
        label="Lorem ipsum"
        options={DUMMY_OPTIONS}
        defaultOption={{ id: 3, value: "Three" }}
        onSelect={jest.fn()}
      />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it('should render a paragraph with the default option when the "readOnly" is set', () => {
    const { asFragment } = render(
      <FieldRadioGroup
        label="Lorem ipsum"
        options={DUMMY_OPTIONS}
        onSelect={jest.fn()}
        defaultOption={DUMMY_OPTIONS[1]}
        readOnly
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
