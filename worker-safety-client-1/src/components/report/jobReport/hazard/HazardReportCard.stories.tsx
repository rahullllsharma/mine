import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";
import type { Hazard } from "@/types/project/Hazard";
import { FormProvider, useForm } from "react-hook-form";
import HazardReportCard from "./HazardReportCard";

export default {
  title: "Components/Report/JobReport/Hazard",
  component: HazardReportCard,
  decorators: [
    Story => (
      <Wrapper>
        <div className="max-w-sm">
          <Story />
        </div>
      </Wrapper>
    ),
  ],
} as ComponentMeta<typeof HazardReportCard>;

const hazard: Hazard = {
  id: "1",
  name: "Pinch Point",
  isApplicable: true,
  controls: [
    { id: "1", name: "Gloves", isApplicable: true },
    { id: "2", name: "Situational Jobsite Awareness", isApplicable: false },
  ],
};

function Wrapper({ children }: PropsWithClassName): JSX.Element {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

const Template: ComponentStory<typeof HazardReportCard> = args => (
  <HazardReportCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  hazard,
};
