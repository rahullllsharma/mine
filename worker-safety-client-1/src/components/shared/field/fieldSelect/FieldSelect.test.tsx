import { render } from "@testing-library/react";
import FieldSelect from "./FieldSelect";

const DUMMY_OPTIONS = [
  { id: 1, name: "One" },
  { id: 2, name: "Two" },
  { id: 3, name: "Three" },
  { id: 4, name: "Four" },
];

describe(FieldSelect.name, () => {
  it('should render with the "Select" component', () => {
    const { asFragment } = render(
      <FieldSelect
        label="Lorem ipsum"
        options={DUMMY_OPTIONS}
        onSelect={jest.fn()}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render a paragraph with the default option when the "readOnly" is set', () => {
    const { asFragment } = render(
      <FieldSelect
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
