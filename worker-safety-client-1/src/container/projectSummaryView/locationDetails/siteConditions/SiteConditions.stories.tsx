import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import SiteConditions from "./SiteConditions";

export default {
  title: "Container/SummaryView/LocationDetails/SiteConditions",
  component: SiteConditions,
} as ComponentMeta<typeof SiteConditions>;

const elements = [
  {
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
        controls: [
          {
            id: "1",
            name: "Replenish Water Supply",
            isApplicable: true,
          },
        ],
      },
    ],
    incidents: [],
  },
];

const TemplateSiteConditions: ComponentStory<typeof SiteConditions> = args => (
  <SiteConditions {...args} />
);

export const SiteConditionCardOpen = TemplateSiteConditions.bind({});

SiteConditionCardOpen.args = {
  elements,
  isCardOpen: () => true,
};

export const SiteConditionCardClose = TemplateSiteConditions.bind({});

SiteConditionCardClose.args = {
  elements,
  isCardOpen: () => false,
};
