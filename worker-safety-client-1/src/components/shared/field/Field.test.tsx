import { render, screen } from "@testing-library/react";
import Field from "./Field";

//TODO Test will probably have to be updated once we start including form validations and controls

describe("Field", () => {
  it('should render a paragraph if the prop "label" is provided', () => {
    render(
      <Field label="Lorem ipsum">
        <input type="text" />
      </Field>
    );
    const labelElement = screen.getByText("Lorem ipsum");
    expect(labelElement).toBeInTheDocument();
  });

  it('should render an " *" next to the label if the props "label" and "required" are provided', () => {
    render(
      <Field label="Lorem ipsum" required>
        <input type="text" />
      </Field>
    );
    const labelElement = screen.getByText("Lorem ipsum *");
    expect(labelElement).toBeInTheDocument();
  });

  it('should render a paragraph if the prop "caption" is provided', () => {
    render(
      <Field caption="Caption text">
        <input type="text" />
      </Field>
    );
    const captionElement = screen.getByText("Caption text");
    expect(captionElement).toBeInTheDocument();
  });

  it('should render two paragraphs if the props "label" and "caption" are provided', () => {
    render(
      <Field label="Lorem ipsum" caption="Caption text">
        <input type="text" />
      </Field>
    );
    expect(screen.queryByText("Lorem ipsum")).toBeInTheDocument();
    expect(screen.queryByText("Caption text")).toBeInTheDocument();
  });
});
