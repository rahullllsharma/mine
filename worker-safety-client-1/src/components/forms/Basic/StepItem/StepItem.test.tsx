import { fireEvent, render, screen } from "@testing-library/react";

import { StepItem } from "./StepItem";

describe(StepItem.name, () => {
  it("renders correctly default step", () => {
    const { asFragment } = render(
      <StepItem label="Test" onClick={jest.fn()} />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly current step", () => {
    const { asFragment } = render(
      <StepItem status="current" label="Test" onClick={jest.fn()} />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly visited step", () => {
    const { asFragment } = render(
      <StepItem status="saved" label="Test" onClick={jest.fn()} />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  describe("user actions", () => {
    it("behaves correctly when user clicks", () => {
      const onClick = jest.fn();
      render(<StepItem label="Test" onClick={onClick} />);

      fireEvent.click(screen.getByRole("button"));

      expect(onClick).toHaveBeenCalledTimes(1);
    });
  });
});
