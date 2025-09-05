import { render, screen, fireEvent } from "@testing-library/react";

import { HazardsSection } from "./HazardsSection";

describe(HazardsSection.name, () => {
  const props = {
    onClickEdit: jest.fn(),
    hazards: [
      "Stuck by equipment",
      "Electrical contact with source",
      "Biological hazards - Insects, animals, poisonous plants",
    ],
  };
  it("renders correctly", () => {
    const { asFragment } = render(<HazardsSection {...props} />);

    expect(asFragment()).toMatchSnapshot();
  });

  describe("user events", () => {
    it("does correct action when user clicks on edit button", () => {
      const onClickEdit = jest.fn();
      render(<HazardsSection {...props} onClickEdit={onClickEdit} />);

      fireEvent.click(screen.getByRole("button"));

      expect(onClickEdit).toHaveBeenCalledTimes(1);
    });
  });
});
