import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import SystemOperatingProcedures from "./SystemOperatingProcedures";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    systemOperatingProcedures: {
      onSiteAndCurrent: "",
      onSiteAndCurrentNotes: "",
      gasControlsNotified: "",
      gasControlsNotifiedNotes: "",
      sopId: "",
      sopType: "",
      sopStepsCalledIn: "",
      sopComments: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    systemOperatingProcedures: {
      onSiteAndCurrent: "0",
      onSiteAndCurrentNotes: "",
      gasControlsNotified: "1",
      gasControlsNotifiedNotes: "",
      sopId: "#11AA22",
      sopType: "-",
      sopStepsCalledIn: "Steps called in",
      sopComments: "No additional comments",
    },
  },
};

describe(SystemOperatingProcedures.name, () => {
  it("should display the SystemOperatingProcedures section without defaults", () => {
    const { asFragment } = formRender(<SystemOperatingProcedures />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SystemOperatingProcedures section with empty state values", () => {
    const { asFragment } = formRender(
      <SystemOperatingProcedures />,
      emptyStateValues
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SystemOperatingProcedures section with prefilled values", () => {
    const { asFragment } = formRender(
      <SystemOperatingProcedures />,
      prefilledValues
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
