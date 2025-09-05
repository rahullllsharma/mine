import type { Control } from "@/types/project/Control";
import type { ControlAnalysisInput } from "@/types/report/DailyReportInputs";
import { screen, fireEvent } from "@testing-library/react";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import ControlReportCard from "./ControlReportCard";

describe("ControlReportCard", () => {
  mockTenantStore();
  it("should render without any selection by default", () => {
    const control: Control = { id: "1", name: "Gloves", isApplicable: false };
    formRender(<ControlReportCard formGroupKey="key" control={control} />);

    const radioElementImplemented = screen.getByLabelText("Implemented");
    expect(radioElementImplemented).not.toBeChecked();
    const radioElementNotImplemented = screen.getByLabelText("Not Implemented");
    expect(radioElementNotImplemented).not.toBeChecked();
  });

  it("should render without Select by default", () => {
    const control: Control = { id: "1", name: "Gloves", isApplicable: false };
    formRender(<ControlReportCard formGroupKey="key" control={control} />);

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it('should show the Select and "Further Explanation" textarea if "Not Implemented" is selected', () => {
    const control: Control = { id: "1", name: "Gloves", isApplicable: false };
    formRender(<ControlReportCard formGroupKey="key" control={control} />);
    const radioElement = screen.getByLabelText("Not Implemented");
    fireEvent.click(radioElement);
    expect(radioElement).toBeChecked();
    expect(screen.queryByRole("button")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).toBeInTheDocument();
  });

  it('should hide the Select and "Further Explanation" textarea if "Implemented" is selected', () => {
    const control: Control = { id: "1", name: "Gloves", isApplicable: true };
    formRender(<ControlReportCard formGroupKey="key" control={control} />);
    const radioElement = screen.getByLabelText("Implemented");
    fireEvent.click(radioElement);
    expect(radioElement).toBeChecked();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  describe("when has control selected", () => {
    it('should render with option "Implemented" selected if control is implemented', () => {
      const control: Control = { id: "1", name: "Gloves", isApplicable: true };
      const selectedControl: ControlAnalysisInput = {
        id: "1",
        implemented: true,
      };
      formRender(
        <ControlReportCard
          formGroupKey="key"
          control={control}
          selectedControl={selectedControl}
        />
      );
      const radioElement = screen.getByLabelText("Implemented");
      expect(radioElement).toBeChecked();
    });

    it('should render with option "Not Implemented" selected if control is not Implemented', () => {
      const selectedControl: ControlAnalysisInput = {
        id: "1",
        implemented: false,
      };
      const control: Control = { id: "1", name: "Gloves", isApplicable: false };
      formRender(
        <ControlReportCard
          formGroupKey="key"
          control={control}
          selectedControl={selectedControl}
        />
      );
      const radioElement = screen.getByLabelText("Not Implemented");
      expect(radioElement).toBeChecked();
    });

    it('should render with option "Not Implemented" selected and its reason if control is not Implemented ', () => {
      const selectedControl: ControlAnalysisInput = {
        id: "1",
        implemented: false,
        notImplementedReason: "Planned but not implemented",
      };
      const control: Control = { id: "1", name: "Gloves", isApplicable: false };
      formRender(
        <ControlReportCard
          formGroupKey="key"
          control={control}
          selectedControl={selectedControl}
        />
      );
      screen.getByText("Planned but not implemented");
      const radioElement = screen.getByLabelText("Not Implemented");
      expect(radioElement).toBeChecked();
    });
  });
});
