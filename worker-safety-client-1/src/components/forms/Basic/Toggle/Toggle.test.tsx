import type { ToggleProps } from "./Toggle";

import { fireEvent, render, screen } from "@testing-library/react";
import { Toggle } from "./Toggle";

describe(Toggle.name, () => {
  let sharedProps: ToggleProps;

  beforeEach(() => {
    sharedProps = {
      disabled: false,
      checked: false,
      onClick: jest.fn(),
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(<Toggle {...sharedProps} />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly when checked", () => {
    const { asFragment } = render(<Toggle {...sharedProps} checked />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly disabled", () => {
    const { asFragment } = render(<Toggle {...sharedProps} disabled />);

    expect(asFragment()).toMatchSnapshot();
  });

  describe("user interaction", () => {
    it("calls proper action when the user clicks", () => {
      render(<Toggle {...sharedProps} />);

      const toggle = screen.getByRole("checkbox");
      fireEvent.click(toggle);

      expect(sharedProps.onClick).toHaveBeenCalledTimes(1);
    });
  });

  // it("renders correctly default layout", () => {
  //   const field = createField();
  //   const { asFragment } = render(<Toggle {...sharedProps} field={field} />);

  //   expect(asFragment()).toMatchSnapshot();
  // });

  // it("renders correctly when hasError", () => {
  //   let field = createField();
  //   field = updateFormField(decodeToggleInput)("");
  //   const { asFragment } = render(<Toggle {...sharedProps} field={field} />);

  //   expect(asFragment()).toMatchSnapshot();
  // });
});
