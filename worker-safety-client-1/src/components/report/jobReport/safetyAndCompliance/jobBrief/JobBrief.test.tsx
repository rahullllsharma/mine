import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import JobBrief from "./JobBrief";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    jobBrief: {
      comprehensiveJobBriefConduct: "",
      comprehensiveJobBriefConductNotes: "",
      jobBriefConductAfterWork: "",
      jobBriefConductAfterWorkNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    jobBrief: {
      comprehensiveJobBriefConduct: "1",
      comprehensiveJobBriefConductNotes: "Conducts notes",
      jobBriefConductAfterWork: "-1",
      jobBriefConductAfterWorkNotes: "After work notes",
    },
  },
};

describe(JobBrief.name, () => {
  it("should display the JobBrief section without defaults", () => {
    const { asFragment } = formRender(<JobBrief />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should render JobBrief section component with empty state values", () => {
    const { asFragment } = formRender(<JobBrief />, emptyStateValues);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should render JobBrief section component with prefilled values", () => {
    const { asFragment } = formRender(<JobBrief />, prefilledValues);
    expect(asFragment()).toMatchSnapshot();
  });
});
