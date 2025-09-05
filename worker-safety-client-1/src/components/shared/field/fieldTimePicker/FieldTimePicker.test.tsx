import { render, screen } from "@testing-library/react";
import FieldTimePicker from "./FieldTimePicker";

describe(FieldTimePicker.name, () => {
  it('should render with the "FieldTimePicker" component', () => {
    const { asFragment } = render(
      <FieldTimePicker name="time-picker" label="Lorem ipsum" />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render the default value passed", () => {
    render(
      <FieldTimePicker
        name="time-picker"
        label="Lorem ipsum"
        defaultValue="10:20"
      />
    );

    screen.getByDisplayValue("10:20");
  });

  it("should render the value passed", () => {
    render(
      <FieldTimePicker name="time-picker" label="Lorem ipsum" value="10:20" />
    );

    screen.getByDisplayValue("10:20");
  });

  it("should be accessable by the label", () => {
    render(
      <FieldTimePicker name="time-picker" label="Lorem ipsum" value="10:20" />
    );

    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveDisplayValue("10:20");
    expect(screen.getByLabelText(/lorem ipsum/i)).toHaveValue("10:20");
  });
});
