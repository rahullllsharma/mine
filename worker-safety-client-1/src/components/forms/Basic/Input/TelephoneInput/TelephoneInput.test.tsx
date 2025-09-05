import type { TelephoneInputProps } from "./TelephoneInput";
import { render, screen, fireEvent } from "@testing-library/react";
import { fieldDef } from "@/utils/formField";
import { validPhoneNumberCodec } from "@/utils/validation";
import { TelephoneInput } from "./TelephoneInput";

describe(TelephoneInput.name, () => {
  let props: TelephoneInputProps<string>;

  beforeEach(() => {
    props = {
      field: fieldDef(validPhoneNumberCodec.decode).init(""),
      onChange: jest.fn(),
      label: "Telephone: *",
    };
  });

  it("renders properly", () => {
    const { asFragment } = render(<TelephoneInput {...props} />);

    expect(screen.getByText("Telephone: *")).toBeInTheDocument();
    expect(asFragment()).toMatchSnapshot();
  });

  describe("user events", () => {
    it("calls onChange when the input changes", () => {
      render(<TelephoneInput {...props} />);

      expect(props.onChange).not.toHaveBeenCalled();

      const input = screen.getByRole("textbox");

      fireEvent.change(input, { target: { value: "1234567890" } });

      expect(props.onChange).toHaveBeenCalledWith("1234567890");
    });
  });
});
