import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { WorkScheduleFormData, WorkScheduleProps } from "./WorkSchedule";
import { useForm } from "react-hook-form";
import { DevTool } from "@hookform/devtools";

import { action } from "@storybook/addon-actions";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { WrapperForm } from "@/utils/dev/storybook";
import WorkSchedule from "./WorkSchedule";

type StoryProps = WorkScheduleProps & { withSubmit?: boolean };

export default {
  title: "Container/Report/WorkSchedule",
  component: WorkSchedule,
  argTypes: {
    withSubmit: { control: "boolean" },
  },
} as ComponentMeta<typeof WorkSchedule>;

const Template: ComponentStory<typeof WorkSchedule> = (args: StoryProps) => {
  // This should be the configuration used on the Report Form
  const methods = useForm({
    mode: "onChange",
    reValidateMode: "onSubmit",
  });

  return (
    <WrapperForm methods={methods}>
      <WorkSchedule {...args} />
      {args.withSubmit && (
        <ButtonPrimary
          type="submit"
          label="Button"
          onClick={methods.handleSubmit((data: WorkScheduleFormData) => {
            action("onSubmit", {})(data);
          })}
        />
      )}
      <DevTool control={methods.control} />
    </WrapperForm>
  );
};

export const Playground = Template.bind({});
Playground.args = {
  endDatetime: "2022-01-19T10:10",
  startDatetime: "2022-01-19T00:00",
  dateLimits: {
    projectStartDate: "2022-01-17",
    projectEndDate: "2022-01-21",
  },
};

export const Readonly = Template.bind({});
Readonly.args = {
  endDatetime: "2022-01-19T20:20",
  startDatetime: "2022-01-19T10:10",
  dateLimits: {
    projectStartDate: "2022-01-17",
    projectEndDate: "2022-01-21",
  },
  isCompleted: true,
};
