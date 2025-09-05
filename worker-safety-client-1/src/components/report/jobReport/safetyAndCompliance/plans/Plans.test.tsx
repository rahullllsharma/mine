import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { screen } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import Plans from "./Plans";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "", membersReviewedAndSignedOff: "" },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "0", membersReviewedAndSignedOff: "1" },
  },
};

describe(Plans.name, () => {
  it("should render Plans section component radiogroup", () => {
    formRender(<Plans />);

    const radioGroup = screen.getAllByRole("radiogroup");
    expect(radioGroup).toHaveLength(2);
  });

  it("should display the plans section with no values", () => {
    const { asFragment } = formRender(<Plans />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the plans section with empty state values", () => {
    const { asFragment } = formRender(<Plans />, emptyStateValues);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the plans section with prefilled values", () => {
    const { asFragment } = formRender(<Plans />, prefilledValues);
    expect(asFragment()).toMatchSnapshot();
  });
});
