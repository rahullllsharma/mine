import type { WorkbookData } from "./providers/spreadsheet";
import type { RenderResult } from "@testing-library/react";
import { render, screen, fireEvent } from "@testing-library/react";
import { nanoid } from "nanoid";
import { sampleRiskCountData } from "./__mocks__/mockData";
import FileDownloadDropdown from "./FileDownloadDropdown";

jest.mock("./providers/spreadsheet", () => {
  return {
    generateDownloadableWorkbook: jest.fn(
      () => new Promise(resolve => setTimeout(() => resolve(true), 500))
    ),
  };
});

const fileTypes = ["XLSX", "CSV"];

const singleWorkbookData = [
  [`worksheet-${nanoid()}`, sampleRiskCountData],
] as WorkbookData;

describe(FileDownloadDropdown.name, () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });
  afterEach(jest.useRealTimers);

  it("should render correctly", () => {
    const { asFragment } = render(
      <FileDownloadDropdown fileName="file" data={singleWorkbookData} />
    );

    screen.getByRole("button", {
      name: /download csv\/xlsx files/i,
    });

    expect(asFragment).toMatchSnapshot();
  });

  it("should render the options to download when the dropdown is clicked", async () => {
    render(<FileDownloadDropdown fileName="file" data={singleWorkbookData} />);

    fireEvent.click(
      screen.getByRole("button", {
        name: /download csv\/xlsx files/i,
      })
    );

    expect(
      await screen.findByRole("menuitem", { name: /export csv/i })
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("menuitem", { name: /export xlsx/i })
    ).toBeInTheDocument();
  });

  it("should disable the action button and display a title explaining why the dropdown is disabled", async () => {
    const title = "";
    render(
      <FileDownloadDropdown
        fileName="file"
        data={singleWorkbookData}
        action={{
          disabled: true,
          title,
        }}
      />
    );

    const $selector = await screen.findByTitle(title);
    expect($selector).toBeDisabled();
  });

  describe.each(fileTypes)("when the menu item %s is clicked", file => {
    let renderedComponent: RenderResult;
    beforeEach(async () => {
      renderedComponent = render(
        <FileDownloadDropdown fileName="file" data={singleWorkbookData} />
      );

      fireEvent.click(
        screen.getByRole("button", {
          name: /download csv\/xlsx files/i,
        })
      );

      await screen.findByRole("menuitem", { name: `Export ${file}` });
    });

    it("should disable the menu item and display a loading spinner besides it", async () => {
      const { asFragment } = renderedComponent;
      fireEvent.click(screen.getByRole("button", { name: `Export ${file}` }));

      // Control the `flow` of the micro task for timers defined on the mocked `generateDownloadableWorkbook` fn
      jest.advanceTimersByTime(50);

      // Assert that BOTH links are disabled
      for (const type of fileTypes) {
        expect(
          await screen.findByRole("button", { name: `Export ${type}` })
        ).toBeDisabled();
      }

      expect(asFragment()).toMatchSnapshot();
    });

    it("should prevent the dropdown from being closed", () => {
      fireEvent.click(screen.getByRole("button", { name: `Export ${file}` }));

      expect(
        screen.queryByRole("menuitem", { name: `Export ${file}` })
      ).toBeInTheDocument();
    });
  });
});
