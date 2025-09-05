import type { ReportSectionBlockProps } from "./ReportSectionBlock";
import { render, screen } from "@testing-library/react";
import ReportSectionBlock from "./ReportSectionBlock";

const withQuestionAndContentProps: ReportSectionBlockProps = {
  children: (
    <>
      <p className="question">Is this a question?</p>
      <p className="content">This is the section block content</p>
    </>
  ),
};

describe(ReportSectionBlock.name, () => {
  it("should render SectionBlock section component with content", () => {
    const { container } = render(
      <ReportSectionBlock {...withQuestionAndContentProps} />
    );
    const question = screen.getByText("Is this a question?");
    const content = container.getElementsByClassName("content");
    expect(question).toBeInTheDocument();
    expect(content).toHaveLength(1);
  });
});
