import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { formRender } from "@/utils/dev/jest";
import SpottersSafetyObserver from "./SpottersSafetyObserver";

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    spottersSafetyObserver: {
      safetyObserverAssigned: "",
      safetyObserverAssignedNotes: "",
      spotterIdentifiedMachineryBackingUp: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    spottersSafetyObserver: {
      safetyObserverAssigned: "0",
      safetyObserverAssignedNotes: "Not yet",
      spotterIdentifiedMachineryBackingUp: "1",
    },
  },
};

describe(SpottersSafetyObserver.name, () => {
  it("should display the SpottersSafetyObserver section without defaults", () => {
    const { asFragment } = formRender(<SpottersSafetyObserver />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SpottersSafetyObserver section with empty state values", () => {
    const { asFragment } = formRender(
      <SpottersSafetyObserver />,
      emptyStateValues
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the SpottersSafetyObserver section with prefilled values", () => {
    const { asFragment } = formRender(
      <SpottersSafetyObserver />,
      prefilledValues
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
