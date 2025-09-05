import { render, screen } from "@testing-library/react";
import PrintReportHeader from "./PrintReportHeader";

describe(PrintReportHeader.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <PrintReportHeader subtitle="this is a subtitle" />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when it renders with a "subtitle"', () => {
    it("should display the subtitle element", () => {
      render(<PrintReportHeader subtitle="This is a subtitle" />);
      screen.getByText("This is a subtitle");
    });
  });
});
