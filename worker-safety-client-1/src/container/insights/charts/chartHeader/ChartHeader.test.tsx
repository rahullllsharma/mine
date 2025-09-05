import type { ComponentProps } from "react";
import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";

import { render, screen } from "@testing-library/react";
import ChartHeader from "./ChartHeader";

const renderComponent = (
  props: ComponentProps<typeof ChartHeader> = {
    title: "title",
    chartData: [],
    chartFilename: "sample-file.ext",
  }
) => {
  return render(<ChartHeader {...props} />, {
    wrapper({ children }) {
      return <>{children}</>;
    },
  });
};

describe(ChartHeader.name, () => {
  const props = {
    title: "header bar title",
    chartFilename: "sample.ext",
    chartData: [["hello", [{ column: "value" }]]] as WorkbookData,
  };

  it("should render correctly", () => {
    const { asFragment } = renderComponent(props);

    expect(asFragment()).toMatchSnapshot();
  });

  it("should match the title passed as the header title", () => {
    renderComponent(props);

    screen.getByRole("heading", {
      name: /header bar title/gi,
      level: 2,
    });
  });

  it("should include the file download dropdown", () => {
    renderComponent(props);

    screen.getByRole("button", {
      name: /download csv\/xlsx files/i,
    });
  });

  describe("when the chart data is empty", () => {
    it("should disable the dropdown action button ", () => {
      const title = "please select a chart";

      renderComponent({
        ...props,
        chartData: [],
        downloadable: true,
        actionTitle: title,
      });

      expect(screen.getByTitle(title)).toBeDisabled();
    });
  });

  describe("when is not downloadable", () => {
    it("should disable the dropdown action button and include a title", () => {
      const title = "please select a chart";
      renderComponent({
        ...props,
        downloadable: false,
        actionTitle: title,
      });

      expect(screen.getByTitle(title)).toBeDisabled();
    });
  });
});
