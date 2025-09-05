import { render, screen } from "@testing-library/react";
import ReportSectionWrapper from "./ReportSectionWrapper";

describe(ReportSectionWrapper.name, () => {
  it("should render ReportSectionWrapper with title only", () => {
    render(
      <ReportSectionWrapper>
        <p>Wrapper children</p>
      </ReportSectionWrapper>
    );
    const wrapperContent = screen.getByText("Wrapper children");
    expect(wrapperContent).toBeInTheDocument();
  });
});
