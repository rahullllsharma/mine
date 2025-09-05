import type { Hazard } from "@/types/project/Hazard";
import type { HazardAnalysisInput } from "@/types/report/DailyReportInputs";
import { screen, fireEvent } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import HazardReportCard from "./HazardReportCard";

const hazard: Hazard = {
  id: "1",
  name: "Pinch Point",
  isApplicable: true,
  controls: [
    { id: "1", name: "Gloves", isApplicable: true },
    { id: "2", name: "Situational Jobsite Awareness", isApplicable: false },
  ],
};

describe("HazardReportCard", () => {
  it('should render with "Applicable" toggled on by default', () => {
    formRender(<HazardReportCard formGroupKey="key" hazard={hazard} />);
    const switchElement = screen.getByRole("switch");
    expect(switchElement).toBeChecked();
  });

  it('should have the same control cards has the ones specified in the "controls" property', () => {
    formRender(<HazardReportCard formGroupKey="key" hazard={hazard} />);
    const controlElements = screen.getAllByTestId("control-report-card-", {
      exact: false,
    });
    expect(controlElements).toHaveLength(hazard.controls.length);
  });

  it("by default, should show all controls (Applicable is on)", () => {
    formRender(<HazardReportCard formGroupKey="key" hazard={hazard} />);
    const controlElements = screen.getAllByTestId("control-report-card-", {
      exact: false,
    });
    expect(controlElements).toHaveLength(hazard.controls.length);
  });

  describe("when Applicable is toggled off", () => {
    beforeEach(() => {
      formRender(<HazardReportCard formGroupKey="key" hazard={hazard} />);
      const switchElement = screen.getByRole("switch");
      fireEvent.click(switchElement);
    });

    it("should hide all controls", () => {
      const controlElements = screen.queryAllByTestId("control-report-card-", {
        exact: false,
      });
      expect(controlElements).toHaveLength(0);
    });
  });

  describe("when has a selected hazard", () => {
    it("should render the switch toggle on when hazard is applicable", () => {
      const selectedHazard = {
        id: hazard.id,
        isApplicable: true,
        controls: [],
      } as HazardAnalysisInput;
      formRender(
        <HazardReportCard
          formGroupKey="key"
          hazard={hazard}
          selectedHazard={selectedHazard}
        />
      );
      expect(screen.getByRole("switch")).toBeChecked();
    });

    it("should render the switch toggle off when hazard is not applicable", () => {
      const selectedHazard = {
        id: hazard.id,
        isApplicable: false,
        controls: [],
      } as HazardAnalysisInput;
      formRender(
        <HazardReportCard
          formGroupKey="key"
          hazard={hazard}
          selectedHazard={selectedHazard}
        />
      );
      expect(screen.getByRole("switch")).not.toBeChecked();
    });
  });
});
