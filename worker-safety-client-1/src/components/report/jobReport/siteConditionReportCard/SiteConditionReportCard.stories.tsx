import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";
import type { HazardAggregator } from "@/types/project/HazardAggregator";
import { FormProvider, useForm } from "react-hook-form";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import SiteConditionReportCard from "./SiteConditionReportCard";

export default {
  title: "Components/Report/SiteConditionReportCard",
  component: SiteConditionReportCard,
  decorators: [
    Story => (
      <Wrapper>
        <div className="max-w-lg" style={{ height: "530px" }}>
          <Story />
        </div>
      </Wrapper>
    ),
  ],
} as ComponentMeta<typeof SiteConditionReportCard>;

const siteCondition: HazardAggregator = {
  id: "1",
  name: "High Heat Index",
  riskLevel: RiskLevel.MEDIUM,
  startDate: "2021-10-10",
  endDate: "2021-10-10",
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

function Wrapper({ children }: PropsWithClassName): JSX.Element {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

const Template: ComponentStory<typeof SiteConditionReportCard> = args => (
  <SiteConditionReportCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  siteCondition,
};
