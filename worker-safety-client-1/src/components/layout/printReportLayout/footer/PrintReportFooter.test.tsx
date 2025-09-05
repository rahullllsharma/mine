import { render, screen } from "@testing-library/react";
import PrintReportFooter from "./PrintReportFooter";

describe(PrintReportFooter.name, () => {
  describe('when it renders without "note" and "pageCount"', () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<PrintReportFooter />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  it("should include an element with the pageNumber class (used in puppeteer)", () => {
    render(<PrintReportFooter />);
    expect(screen.getByTestId("print-report-footer-pagination")).toHaveClass(
      "pageNumber"
    );
  });

  describe('when it renders with "note"', () => {
    it("should display the note element", () => {
      render(<PrintReportFooter note="This is a note" />);
      screen.getByText("This is a note");
    });
  });
});
