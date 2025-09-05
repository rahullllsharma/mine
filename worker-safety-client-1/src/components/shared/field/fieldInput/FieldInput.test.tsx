import { render } from "@testing-library/react";
import FieldInput from "./FieldInput";

describe("FieldInput", () => {
  it('should render with the "input" component', () => {
    const { asFragment } = render(
      <FieldInput
        htmlFor="lorem"
        id="lorem"
        label="Lorem ipsum"
        placeholder="Lorem ipsum"
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
