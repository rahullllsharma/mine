import { render, screen, fireEvent } from "@testing-library/react";
import FieldTextArea from "./FieldTextArea";

const textChangeHandler = jest.fn();

describe("FieldTextArea", () => {
  it('should render with the "TextArea" component', () => {
    const { asFragment } = render(
      <FieldTextArea label="Lorem ipsum" onChange={textChangeHandler} />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should display an initial text if "initialValue" prop is set with a value', () => {
    render(
      <FieldTextArea
        label="Lorem ipsum"
        name="some-name"
        onChange={textChangeHandler}
        initialValue="initial textbox value"
      />
    );
    const textElement = screen.getByRole("textbox");
    expect(textElement.textContent).toBe("initial textbox value");
  });

  it("should update the text area when user types", () => {
    render(<FieldTextArea label="Lorem ipsum" onChange={textChangeHandler} />);
    const textElement = screen.getByRole("textbox");
    fireEvent.change(textElement, { target: { value: "This is some text" } });
    expect(textElement).toHaveValue("This is some text");
  });

  it('should be disabled if "isDisabled" prop is set to true', () => {
    render(
      <FieldTextArea
        label="Lorem ipsum"
        onChange={textChangeHandler}
        isDisabled
      />
    );
    const textElement = screen.getByRole("textbox");
    expect(textElement).toBeDisabled();
  });

  it('should call the "onChange" callback when "onChange" event is triggered', () => {
    render(<FieldTextArea label="Lorem ipsum" onChange={textChangeHandler} />);
    const textElement = screen.getByRole("textbox");
    fireEvent.change(textElement, { target: { value: "This is some text" } });
    expect(textChangeHandler).toHaveBeenCalledWith("This is some text");
  });

  it("should have a placeholder", () => {
    render(
      <FieldTextArea
        label="Lorem ipsum"
        placeholder="sit amet"
        onChange={textChangeHandler}
      />
    );
    screen.getByPlaceholderText(/sit amet/i);
  });

  it('should be readonly and not have borders if the property "readOnly" is set', () => {
    const { asFragment } = render(
      <FieldTextArea
        readOnly
        initialValue="Lorem ipsum"
        name="some-name"
        onChange={textChangeHandler}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it('should render a red border in the textarea if the prop "hasError" is set', () => {
    render(
      <FieldTextArea
        label="Lorem ipsum"
        placeholder="sit amet"
        onChange={textChangeHandler}
        hasError
      />
    );
    const textElement = screen.getByRole("textbox");
    expect(textElement).toHaveClass(
      "border-system-error-40 focus-within:ring-system-error-40"
    );
  });
});
