import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import WorkMethods from "./WorkMethods";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    workMethods: { contractorAccess: "", contractorAccessNotes: "" },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    workMethods: {
      contractorAccess: "0",
      contractorAccessNotes: "Not granted",
    },
  },
};

describe(WorkMethods.name, () => {
  mockTenantStore();
  it("should display the WorkMethods section without defaults", () => {
    const { asFragment } = formRender(<WorkMethods />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the WorkMethods section with empty state values", () => {
    const { asFragment } = formRender(<WorkMethods />, emptyStateValues);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the WorkMethods section with prefilled values", () => {
    const { asFragment } = formRender(<WorkMethods />, prefilledValues);
    expect(asFragment()).toMatchSnapshot();
  });
});
