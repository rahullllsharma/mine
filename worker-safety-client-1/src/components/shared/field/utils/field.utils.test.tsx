import { render } from "@testing-library/react";
import Field from "../Field";
import { scrollToFirstErrorSection } from "./field.utils";

describe("Field Utils", () => {
  const scrollIntoViewMock = jest.fn();

  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;
  });

  it("should not fire scrollIntoView when there are no errors in DOM", () => {
    render(
      <>
        <Field label="Input 1">
          <input type="text" />
        </Field>
        <Field label="Input 2">
          <input type="text" />
        </Field>
        <Field label="Input 3">
          <input type="text" />
        </Field>
      </>
    );

    scrollToFirstErrorSection();

    expect(scrollIntoViewMock).toHaveBeenCalledTimes(0);
  });

  it("should fire scrollIntoView", () => {
    render(
      <>
        <Field label="Input 1">
          <input type="text" />
        </Field>
        <Field label="Input 2" error="sample error">
          <input type="text" />
        </Field>
        <Field label="Input 3">
          <input type="text" />
        </Field>
      </>
    );

    scrollToFirstErrorSection();

    expect(scrollIntoViewMock).toHaveBeenCalled();
  });
});
