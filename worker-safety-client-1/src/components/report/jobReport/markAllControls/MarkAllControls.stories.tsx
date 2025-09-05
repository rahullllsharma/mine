import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";
import type { HazardAggregator } from "@/types/project/HazardAggregator";
import { FormProvider, useForm } from "react-hook-form";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import { MarkAllControls } from "./MarkAllControls";

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

function Wrapper({ children }: PropsWithClassName): JSX.Element {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

export default {
  title: "Components/Report/MarkAllControls",
  component: MarkAllControls,
  decorators: [
    Story => (
      <Wrapper>
        <div className="max-w-lg h-screen overflow-auto p-1">
          <Story />
        </div>
      </Wrapper>
    ),
  ],
} as ComponentMeta<typeof MarkAllControls>;

const Template: ComponentStory<typeof MarkAllControls> = args => (
  <MarkAllControls {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  element: siteCondition,
  formGroupKey: "siteConditions",
};
