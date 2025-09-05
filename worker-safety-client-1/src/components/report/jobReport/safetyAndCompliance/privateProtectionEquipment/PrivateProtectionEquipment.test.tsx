import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import PrivateProtectionEquipment from "./PrivateProtectionEquipment";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    privateProtectionEquipment: {
      wearingPPE: "",
      wearingPPENotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    privateProtectionEquipment: {
      wearingPPE: "0",
      wearingPPENotes:
        "No security/protection measures applied to any crew member nor visitors",
    },
  },
};

describe(PrivateProtectionEquipment.name, () => {
  it("should display the PrivateProtectionEquipment section without defaults", () => {
    const { asFragment } = formRender(<PrivateProtectionEquipment />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the PrivateProtectionEquipment section with empty state values", () => {
    const { asFragment } = formRender(
      <PrivateProtectionEquipment />,
      emptyStateValues
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the PrivateProtectionEquipment section with prefilled values", () => {
    const { asFragment } = formRender(
      <PrivateProtectionEquipment />,
      prefilledValues
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
