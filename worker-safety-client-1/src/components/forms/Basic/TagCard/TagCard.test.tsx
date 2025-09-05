import { render, screen } from "@testing-library/react";

import { TagCard } from "./TagCard";

describe(TagCard.name, () => {
  it("renders correctly", () => {
    render(
      <TagCard>
        <p>Traffic density</p>
      </TagCard>
    );

    expect(screen.getByText("Traffic density")).toBeInTheDocument();
  });
});
