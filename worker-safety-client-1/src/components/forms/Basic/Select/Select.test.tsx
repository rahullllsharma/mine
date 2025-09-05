import type { SelectProps } from "./Select";
import { fireEvent, render, screen } from "@testing-library/react";

import { none, some } from "fp-ts/lib/Option";
import * as O from "fp-ts/lib/Option";
import { Select } from "./Select";

describe(Select.name, () => {
  let props: SelectProps<string, string>;

  beforeEach(() => {
    props = {
      options: [
        { label: "Option 1", value: "option1" },
        { label: "Option 2", value: "option 2" },
      ],
      selected: none,
      placeholder: "Choose a contact",
      onSelected: jest.fn(),
      optionKey: jest.fn(),
      renderLabel: jest.fn(label => <>{label}</>),
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(<Select {...props} />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with label", () => {
    render(<Select {...props} label="Contact:" />);

    expect(screen.getByText("Contact:")).toBeInTheDocument();
  });

  it("renders correctly with an option selected", () => {
    render(<Select {...props} selected={some("option1")} />);

    expect(screen.getByText("Option 1")).toBeInTheDocument();
  });

  describe("User interactions", () => {
    it("opens options when user clicks", () => {
      const { asFragment } = render(<Select {...props} />);

      const select = screen.getByText("Choose a contact");
      fireEvent.click(select);

      expect(screen.getByText("Option 1")).toBeInTheDocument();
      expect(screen.getByText("Option 2")).toBeInTheDocument();
      expect(asFragment()).toMatchSnapshot();
    });

    it("does select action when user selects an option", () => {
      render(<Select {...props} />);

      const select = screen.getByText("Choose a contact");
      fireEvent.click(select);
      const option1 = screen.getByText("Option 1");
      fireEvent.click(option1);

      expect(props.onSelected).toHaveBeenCalledWith(O.some("option1"));
    });
  });
});
