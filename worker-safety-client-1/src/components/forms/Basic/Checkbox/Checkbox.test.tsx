import type { CheckboxProps } from "./Checkbox";

import { fireEvent, render, screen } from "@testing-library/react";
import { Checkbox } from "./Checkbox";

describe(Checkbox.name, () => {
  let sharedProps: CheckboxProps;

  beforeEach(() => {
    sharedProps = {
      onClick: jest.fn(),
      checked: false,
      disabled: false,
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(
      <Checkbox {...sharedProps}>Option 1</Checkbox>
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly when is checked", () => {
    const { asFragment } = render(
      <Checkbox {...sharedProps} checked>
        Option 1
      </Checkbox>
    );

    expect(asFragment()).toMatchSnapshot();
  });

  describe("User interaction", () => {
    it("calls the correct action when users clicks", () => {
      render(
        <Checkbox {...sharedProps} checked>
          Option 1
        </Checkbox>
      );

      const checkbox = screen.getByRole("checkbox");
      fireEvent.click(checkbox);

      expect(sharedProps.onClick).toHaveBeenCalledTimes(1);
    });
  });

  // it("renders correctly", () => {
  //   const field = createFormField("", decodeFunction);
  //   const { asFragment } = render(
  //     <Checkbox {...sharedProps} field={field}>
  //       Test
  //     </Checkbox>
  //   );

  //   expect(screen.getByText("Test")).toBeInTheDocument();
  //   expect(asFragment()).toMatchSnapshot();
  // });

  // it("renders correctly with error", () => {
  //   let field = createFormField("", decodeFunction);
  //   field = updateFormField(decodeFunction)("");

  //   const { asFragment } = render(
  //     <Checkbox {...sharedProps} field={field}>
  //       Test
  //     </Checkbox>
  //   );

  //   expect(screen.getByText("Please choose an option"));
  //   expect(asFragment()).toMatchSnapshot();
  // });
});
