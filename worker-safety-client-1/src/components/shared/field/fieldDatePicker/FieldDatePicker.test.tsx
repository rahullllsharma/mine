import { render, screen } from "@testing-library/react";
import FieldDatePicker from "./FieldDatePicker";

describe(FieldDatePicker.name, () => {
  it('should render with the "FieldDatePicker" component', () => {
    const { asFragment } = render(
      <FieldDatePicker name="date-picker" label="Lorem ipsum" />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render the default value passed", () => {
    render(
      <FieldDatePicker
        name="date-picker"
        label="Lorem ipsum"
        defaultValue="2021-12-17"
      />
    );

    screen.getByDisplayValue("2021-12-17");
  });

  it("should render the value passed", () => {
    render(
      <FieldDatePicker
        name="date-picker"
        label="Lorem ipsum"
        value="2021-12-17"
      />
    );

    screen.getByDisplayValue("2021-12-17");
  });

  it("should be accessable by the label", () => {
    render(
      <FieldDatePicker
        name="date-picker"
        label="Lorem ipsum"
        value="2021-12-17"
      />
    );

    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveDisplayValue(
      "2021-12-17"
    );
    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveValue("2021-12-17");
  });
});
