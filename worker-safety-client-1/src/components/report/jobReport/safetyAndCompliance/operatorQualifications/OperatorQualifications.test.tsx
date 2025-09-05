import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import OperatorQualifications from "./OperatorQualifications";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    operatorQualifications: {
      qualificationsVerified: "",
      qualificationsVerifiedNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    operatorQualifications: {
      qualificationsVerified: "1",
      qualificationsVerifiedNotes: "All ok",
    },
  },
};

describe(OperatorQualifications.name, () => {
  it("should display the OperatorQualifications section without defaults", () => {
    const { asFragment } = formRender(<OperatorQualifications />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the OperatorQualifications section with empty state values", () => {
    const { asFragment } = formRender(
      <OperatorQualifications />,
      emptyStateValues
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the OperatorQualifications section with prefilled values", () => {
    const { asFragment } = formRender(
      <OperatorQualifications />,
      prefilledValues
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
