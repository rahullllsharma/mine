import type { HazardAggregator } from "@/types/project/HazardAggregator";
import { screen, fireEvent, act } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import { TaskStatus } from "@/types/task/TaskStatus";
import SiteConditionReportCard from "./SiteConditionReportCard";

const siteCondition: HazardAggregator = {
  id: "1",
  name: "High Heat Index",
  riskLevel: RiskLevel.MEDIUM,
  startDate: "2021-10-10",
  endDate: "2021-10-11",
  status: TaskStatus.NOT_STARTED,
  isManuallyAdded: false,
  hazards: [
    {
      id: "1",
      name: "Dehydration",
      isApplicable: true,
      controls: [{ id: "1", name: "Dehydration", isApplicable: true }],
    },
  ],
  incidents: [],
};

describe("SiteConditionsReportCard", () => {
  mockTenantStore();
  beforeEach(() => {
    formRender(<SiteConditionReportCard siteCondition={siteCondition} />);
  });

  it('should display the switch button with "Applicable" text', () => {
    const switchElement = screen.getByRole("switch", { name: /applicable/i });
    expect(switchElement.textContent).toBe("Applicable?");
  });

  describe("when a Site Condition is not Applicable", () => {
    it("should only have the switch turned off", () => {
      const switchElement = screen.getByRole("switch", { name: /applicable/i });
      fireEvent.click(switchElement);
      expect(switchElement).toHaveAttribute("aria-checked", "false");
    });

    // We may need to re-enable in the future.
    xit('should render a select with the title "Why is this site condition not applicable?"', () => {
      const switchElement = screen.getByRole("switch", { name: /applicable/i });
      fireEvent.click(switchElement);
      screen.getByText("Why is this site condition not applicable?", {
        exact: false,
      });
    });
  });

  describe('when "Mark all controls as implemented" is unchecked', () => {
    it('should render a "Mark all controls as implemented" checkbox', () => {
      formRender(<SiteConditionReportCard siteCondition={siteCondition} />);
      screen.getByRole("checkbox", {
        name: /mark all controls as implemented/i,
      });
    });

    it('should have at least one control as "not implemented"', () => {
      formRender(<SiteConditionReportCard siteCondition={siteCondition} />);
      screen.getAllByRole("radio", { checked: false });
    });

    describe('when "Mark all controls as implemented" is clicked', () => {
      it("should set all the controls as implemented", () => {
        act(() => {
          formRender(<SiteConditionReportCard siteCondition={siteCondition} />);
          fireEvent.click(
            screen.getByRole("checkbox", {
              name: /mark all controls as implemented/i,
              checked: false,
            })
          );
        });

        act(() => {
          screen.getByRole("checkbox", {
            name: /mark all controls as implemented/i,
            checked: true,
          });
        });

        const elements = screen.getAllByRole("radio", {
          name: /implemented/i,
          checked: true,
        });

        const totalControls = siteCondition.hazards.reduce(
          (acc, hazard) => acc + hazard.controls.length,
          0
        );
        expect(elements).toHaveLength(totalControls);
      });
    });
  });
});
