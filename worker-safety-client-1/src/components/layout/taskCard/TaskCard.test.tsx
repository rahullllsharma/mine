import { render, screen } from "@testing-library/react";
import TaskCard from "./TaskCard";

describe("TaskCard", () => {
  const header = "Above Ground Welding";
  const content = "Above Ground Welding content";

  it("should render a header", () => {
    render(<TaskCard taskHeader={header} />);
    screen.getByText(header);
  });

  describe("when card is open", () => {
    describe("when contain a task content", () => {
      it("should render the content", () => {
        render(<TaskCard taskHeader={header}>{content}</TaskCard>);
        screen.getByText(content);
      });
    });
  });

  describe("when card is closed", () => {
    describe("when contain a task content", () => {
      it("should not be visible", () => {
        render(
          <TaskCard taskHeader={header} isOpen={false}>
            {content}
          </TaskCard>
        );
        const element = screen.queryByText(content);
        expect(element).not.toBeInTheDocument();
      });
    });
  });

  describe("when contain a task content", () => {
    it("should be visible when card is opened", () => {
      render(<TaskCard taskHeader={header}>{content}</TaskCard>);
      screen.getByText(content);
    });
    it("should not be visible when card is closed", () => {
      render(
        <TaskCard taskHeader={header} isOpen={false}>
          {content}
        </TaskCard>
      );
      const element = screen.queryByText(content);
      expect(element).not.toBeInTheDocument();
    });
  });
});
