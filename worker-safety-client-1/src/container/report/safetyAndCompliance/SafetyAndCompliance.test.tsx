import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import SafetyAndCompliance from "./SafetyAndCompliance";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "", membersReviewedAndSignedOff: "" },
    jobBrief: {
      comprehensiveJobBriefConduct: "",
      comprehensiveJobBriefConductNotes: "",
      jobBriefConductAfterWork: "",
      jobBriefConductAfterWorkNotes: "",
    },
    workMethods: { contractorAccess: "", contractorAccessNotes: "" },
    digSafeMarkOuts: {
      markOutsVerified: "",
      markOutsVerifiedNotes: "",
      facilitiesLocatedAndExposed: "",
      facilitiesLocatedAndExposedNotes: "",
      digSafeMarkOutsLocation: "",
    },
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
    spottersSafetyObserver: {
      safetyObserverAssigned: "",
      safetyObserverAssignedNotes: "",
      spotterIdentifiedMachineryBackingUp: "",
    },
    privateProtectionEquipment: {
      wearingPPE: "",
      wearingPPENotes: "",
    },
    operatorQualifications: {
      qualificationsVerified: "",
      qualificationsVerifiedNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "1", membersReviewedAndSignedOff: "1" },
    jobBrief: {
      comprehensiveJobBriefConduct: "1",
      comprehensiveJobBriefConductNotes: "Conducts notes",
      jobBriefConductAfterWork: "-1",
      jobBriefConductAfterWorkNotes: "After work notes",
    },
    workMethods: {
      contractorAccess: "0",
      contractorAccessNotes: "Not granted",
    },
    digSafeMarkOuts: {
      markOutsVerified: "-1",
      markOutsVerifiedNotes: "N/A",
      facilitiesLocatedAndExposed: "1",
      facilitiesLocatedAndExposedNotes: "Yes",
      digSafeMarkOutsLocation: "No additional notes",
    },
    systemOperatingProcedures: {
      onSiteAndCurrent: "0",
      onSiteAndCurrentNotes: "On-site and current notes",
      gasControlsNotified: "1",
      gasControlsNotifiedNotes: "Gas control notification notes",
      sopId: "#11AA22",
      sopType: "Unknown",
      sopStepsCalledIn: "Steps called in",
      sopComments: "No additional comments",
    },
    spottersSafetyObserver: {
      safetyObserverAssigned: "0",
      safetyObserverAssignedNotes: "Not yet",
      spotterIdentifiedMachineryBackingUp: "1",
    },
    privateProtectionEquipment: {
      wearingPPE: "0",
      wearingPPENotes:
        "No security/protection measures applied to any crew member nor visitors",
    },
    operatorQualifications: {
      qualificationsVerified: "1",
      qualificationsVerifiedNotes: "All ok",
    },
  },
};

describe(SafetyAndCompliance.name, () => {
  mockTenantStore();
  it("should display the SafetyAndCompliance section without defaults", () => {
    const { asFragment } = formRender(<SafetyAndCompliance />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SafetyAndCompliance section with empty state values", () => {
    const { asFragment } = formRender(
      <SafetyAndCompliance />,
      emptyStateValues
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SafetyAndCompliance section with prefilled values", () => {
    const { asFragment } = formRender(<SafetyAndCompliance />, prefilledValues);
    expect(asFragment()).toMatchSnapshot();
  });
});
