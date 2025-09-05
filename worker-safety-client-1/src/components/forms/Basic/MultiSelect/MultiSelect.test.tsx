import type { MultiSelectProps } from "./MultiSelect";
import { render, screen, fireEvent } from "@testing-library/react";

import { MultiSelect } from "./MultiSelect";

describe(MultiSelect.name, () => {
  let props: MultiSelectProps<string, string>;

  beforeEach(() => {
    props = {
      options: [
        {
          label: "Option 1",
          value: "option1",
        },
        {
          label: "Option 2",
          value: "option2",
        },
      ],
      placeholder: "Choose a contact",
      selected: [],
      onRemoved: jest.fn(),
      onSelected: jest.fn(),
      optionKey: jest.fn(),
      renderLabel: jest.fn(label => label),
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(<MultiSelect {...props} />);

    expect(screen.getByText("Choose a contact")).toBeInTheDocument();
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with label", () => {
    render(<MultiSelect {...props} label="Contact:" />);

    expect(screen.getByText("Contact:")).toBeInTheDocument();
  });

  it("renders correctly with 1 selected option", () => {
    render(<MultiSelect {...props} selected={["option1"]} />);

    expect(screen.getByText("Option 1")).toBeInTheDocument();
  });

  it("renders correctly with more than 1 selected option", () => {
    render(<MultiSelect {...props} selected={["option1", "option2"]} />);

    expect(screen.getByText("Option 1")).toBeInTheDocument();
    expect(screen.getByText("Option 2")).toBeInTheDocument();
  });

  describe("User interactions", () => {
    it("opens options when user click", () => {
      const { asFragment } = render(<MultiSelect {...props} />);

      const select = screen.getByText("Choose a contact");
      fireEvent.click(select);

      expect(screen.getByText("Option 1")).toBeInTheDocument();
      expect(screen.getByText("Option 2")).toBeInTheDocument();
      expect(asFragment()).toMatchSnapshot();
    });

    it("does select action when user selects an option", () => {
      render(<MultiSelect {...props} />);

      const select = screen.getByText("Choose a contact");
      fireEvent.click(select);
      const option1 = screen.getByText("Option 1");
      fireEvent.click(option1);

      expect(props.onSelected).toHaveBeenCalledWith("option1");
    });

    it("does delete action when user deletes one option selected", () => {
      const onOuterClick = jest.fn();

      render(
        <div onClick={onOuterClick}>
          <MultiSelect {...props} selected={["option1"]} />
        </div>
      );

      const deleteOptionButton = screen.getByTestId("option1-remove");
      fireEvent.click(deleteOptionButton, event);

      expect(props.onRemoved).toHaveBeenCalledWith("option1");
      expect(onOuterClick).not.toHaveBeenCalled();
    });

    it("keeps the dropdown open after selecting an option", () => {
      render(<MultiSelect {...props} />);

      const select = screen.getByText("Choose a contact");
      fireEvent.click(select);
      const option1 = screen.getByText("Option 1");
      fireEvent.click(option1);

      expect(screen.getByText("Option 1")).toBeInTheDocument();
      expect(screen.getByText("Option 2")).toBeInTheDocument();
    });
  });
});
