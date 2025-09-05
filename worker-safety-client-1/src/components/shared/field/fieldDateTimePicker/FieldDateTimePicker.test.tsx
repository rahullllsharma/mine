import { render, screen } from "@testing-library/react";
import FieldDateTimePicker from "./FieldDateTimePicker";

describe(FieldDateTimePicker.name, () => {
  it('should render with the "FieldDateTimePicker" component', () => {
    const { asFragment } = render(
      <FieldDateTimePicker name="datetime-picker" label="Lorem ipsum" />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render the default value passed", () => {
    render(
      <FieldDateTimePicker
        name="datetime-picker"
        label="Lorem ipsum"
        defaultValue="2022-01-11T10:20"
      />
    );

    screen.getByDisplayValue("2022-01-11T10:20");
  });

  it("should render the value passed", () => {
    render(
      <FieldDateTimePicker
        name="datetime-picker"
        label="Lorem ipsum"
        value="2022-01-11T10:20"
      />
    );

    screen.getByDisplayValue("2022-01-11T10:20");
  });

  it("should be accessable by a label", () => {
    render(
      <FieldDateTimePicker
        name="datetime-picker"
        label="Lorem ipsum"
        value="2022-01-11T10:20"
      />
    );

    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveDisplayValue(
      "2022-01-11T10:20"
    );
    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveValue(
      "2022-01-11T10:20"
    );
  });
});
