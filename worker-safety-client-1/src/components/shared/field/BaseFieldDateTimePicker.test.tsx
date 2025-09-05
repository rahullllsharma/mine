import { fireEvent, render, screen } from "@testing-library/react";
import BaseFieldDateTimePicker, {
  iconByInputType,
} from "./BaseFieldDateTimePicker";

type IconByInputTypeKeys = keyof typeof iconByInputType;

describe(BaseFieldDateTimePicker.name, () => {
  it("should render a Field and an Input", () => {
    render(
      <BaseFieldDateTimePicker type="date" label="Lorem ipsum" name="date" />
    );

    screen.getByText("Lorem ipsum");
    screen.getByLabelText("Lorem ipsum");
  });

  it("should display a default value", () => {
    render(
      <BaseFieldDateTimePicker
        name="date"
        type="date"
        label="Lorem ipsum"
        defaultValue="2022-01-01"
      />
    );

    screen.getByDisplayValue("2022-01-01");
  });

  it("should use the value as default value if defaultValue not passed", () => {
    render(
      <BaseFieldDateTimePicker
        name="date"
        type="date"
        label="Lorem ipsum"
        value="2022-01-01"
      />
    );
    screen.getByDisplayValue("2022-01-01");
  });

  it.each(Object.keys(iconByInputType) as IconByInputTypeKeys[])(
    "should display the proper icon",
    type => {
      render(<BaseFieldDateTimePicker type={type} label={type} name={type} />);
      screen.getByLabelText(type);
      expect(document.querySelector("[aria-hidden]")?.classList.value).toEqual(
        expect.stringContaining(`ci-${iconByInputType[type]}`)
      );
    }
  );

  it("should call the onChange event when the input is modified", () => {
    const mockOnChange = jest.fn();
    render(
      <BaseFieldDateTimePicker
        type="date"
        label="date"
        name="date"
        onChange={mockOnChange}
        defaultValue="2022-01-01"
      />
    );
    screen.getByDisplayValue("2022-01-01");

    fireEvent.change(screen.getByLabelText(/date/i), {
      target: { value: "2022-01-02" },
    });

    expect(mockOnChange).toHaveBeenCalledWith("2022-01-02");
    screen.getByDisplayValue("2022-01-02");
  });

  describe("when is disabled", () => {
    it("should render a generic BaseFieldDateTimePicker disabled", () => {
      render(
        <BaseFieldDateTimePicker
          name="date"
          type="date"
          label="Lorem ipsum"
          value="2022-01-01"
          disabled
        />
      );

      expect(screen.getByDisplayValue("2022-01-01")).toBeDisabled();
    });
  });

  describe("when is read only", () => {
    it("should render the input as text", () => {
      render(
        <BaseFieldDateTimePicker
          name="date"
          type="date"
          label="Lorem ipsum"
          value="2022-01-01"
          readOnly
        />
      );

      expect(screen.getByDisplayValue("2022-01-01")).toBeInTheDocument();
    });
  });
});
