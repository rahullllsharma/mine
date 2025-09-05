import { fireEvent, render, screen } from "@testing-library/react";
import Accordion from "./Accordion";

describe("Accordion", () => {
  describe("when Accordion renders", () => {
    const header = "Accordion header content";
    const panel = "Accordion panel content";

    it("should contain a header", () => {
      const { getByRole } = render(
        <Accordion header={header}>{panel}</Accordion>
      );

      expect(getByRole("button")?.textContent).toBe(header);
    });

    it("should not render the content panel", () => {
      const { queryByText } = render(
        <Accordion header={header}>{panel}</Accordion>
      );

      expect(queryByText(panel)).not.toBeInTheDocument();
    });

    it("should show content panel for selected header when header is clicked", () => {
      const { getByText, getByRole } = render(
        <Accordion header={header}>{panel}</Accordion>
      );
      fireEvent.click(getByRole("button"));
      expect(getByText(panel)).toBeVisible();
    });

    it("should show content panel when header is clicked with animation", async () => {
      render(
        <Accordion header={header} animation="pop">
          {panel}
        </Accordion>
      );
      fireEvent.click(screen.getByRole("button"));
      expect(await screen.findByText(panel)).toBeVisible();
    });

    describe("when is open by default", () => {
      it("should render the content panel", () => {
        const { queryByText } = render(
          <Accordion header={header} isDefaultOpen={true}>
            {panel}
          </Accordion>
        );

        expect(queryByText(panel)).toBeInTheDocument();
      });
    });
  });
});
