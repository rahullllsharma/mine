import type { ReportSectionHeaderProps } from "./ReportSectionHeader";
import { render, screen } from "@testing-library/react";
import ReportSectionHeader from "./ReportSectionHeader";

const reportSectionHeaderWithTitleProps: ReportSectionHeaderProps = {
  title: "Title",
};

const reportSectionHeaderWithTitleAndSubtitleProps: ReportSectionHeaderProps = {
  title: "title",
  subtitle: "Subtitle",
};

describe(ReportSectionHeader.name, () => {
  it("should render SectionHeader with title only", () => {
    render(<ReportSectionHeader {...reportSectionHeaderWithTitleProps} />);
    const titleHeading = screen.getByRole("heading", { level: 5 });
    expect(titleHeading).toBeInTheDocument();
  });

  it("should render SectionHeader with both title and subtitle", () => {
    render(
      <ReportSectionHeader {...reportSectionHeaderWithTitleAndSubtitleProps} />
    );
    const titleHeading = screen.getByRole("heading", { level: 5 });
    const subtitleHeading = screen.getByRole("heading", { level: 6 });
    expect(titleHeading).toBeInTheDocument();
    expect(subtitleHeading).toBeInTheDocument();
  });
});
