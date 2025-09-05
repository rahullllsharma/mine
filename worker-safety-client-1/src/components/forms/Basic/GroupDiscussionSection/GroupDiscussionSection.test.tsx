import { render, fireEvent, screen } from "@testing-library/react";

import { GroupDiscussionSection } from "./GroupDiscussionSection";

describe(GroupDiscussionSection.name, () => {
  const props = {
    title: "Job Information",
    onClickEdit: jest.fn(),
  };

  it("renders correctly", () => {
    const { asFragment } = render(
      <GroupDiscussionSection {...props}>
        <p>Example</p>
      </GroupDiscussionSection>
    );

    expect(asFragment()).toMatchSnapshot();
  });

  describe("user events", () => {
    it("do the correct action when user clicks on edit button", () => {
      const onClickEdit = jest.fn();
      render(
        <GroupDiscussionSection {...props} onClickEdit={onClickEdit}>
          <p>Example</p>
        </GroupDiscussionSection>
      );

      fireEvent.click(screen.getByRole("button"));

      expect(onClickEdit).toHaveBeenCalledTimes(1);
    });
  });
});
