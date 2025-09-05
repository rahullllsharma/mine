import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import DigSafeMarkOuts from "./DigSafeMarkOuts";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    digSafeMarkOuts: {
      markOutsVerified: "",
      markOutsVerifiedNotes: "",
      facilitiesLocatedAndExposed: "",
      facilitiesLocatedAndExposedNotes: "",
      digSafeMarkOutsLocation: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    digSafeMarkOuts: {
      markOutsVerified: "-1",
      markOutsVerifiedNotes: "N/A",
      facilitiesLocatedAndExposed: "1",
      facilitiesLocatedAndExposedNotes: "Yes",
      digSafeMarkOutsLocation: "No additional notes",
    },
  },
};

describe(DigSafeMarkOuts.name, () => {
  it("should display the DigsafeMarkOuts section without defaults", () => {
    const { asFragment } = formRender(<DigSafeMarkOuts />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the DigsafeMarkOuts section with empty state values", () => {
    const { asFragment } = formRender(<DigSafeMarkOuts />, emptyStateValues);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the DigsafeMarkOuts section with prefilled values", () => {
    const { asFragment } = formRender(<DigSafeMarkOuts />, prefilledValues);
    expect(asFragment()).toMatchSnapshot();
  });
});
