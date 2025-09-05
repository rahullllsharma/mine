import { render, screen } from "@testing-library/react";
import EmptyContent from "./EmptyContent";

describe(EmptyContent.name, () => {
  describe("when it renders", () => {
    it("should contain a title", () => {
      render(
        <EmptyContent
          title="This is the title"
          description="This is the description"
        />
      );
      screen.getByText(/this is the title/i);
    });

    it("should contain a description", () => {
      render(
        <EmptyContent
          title="This is the title"
          description="This is a description"
        />
      );
      screen.getByText(/this is a description/i);
    });
  });
});
