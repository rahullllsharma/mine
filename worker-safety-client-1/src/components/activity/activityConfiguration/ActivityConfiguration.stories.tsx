import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { ActivityInputs } from "@/container/activity/addActivityModal/AddActivityModal";
import type { ActivityTypeLibrary } from "@/types/activity/ActivityTypeLibrary";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ActivityConfiguration from "./ActivityConfiguration";

export default {
  title: "Components/Activity/ActivityConfiguration",
  component: ActivityConfiguration,
} as ComponentMeta<typeof ActivityConfiguration>;

const minStartDate = "2022-07-07";
const maxEndDate = "2022-09-09";

const activityTypeLibrary: ActivityTypeLibrary[] = [
  {
    id: "1",
    name: "Activity type 1",
  },
  {
    id: "2",
    name: "Activity type 2",
  },
  {
    id: "3",
    name: "Activity type 3",
  },
];

const Template: ComponentStory<typeof ActivityConfiguration> = args => {
  const form = useForm<ActivityInputs>({
    mode: "onChange",
    defaultValues: {
      name: "Default Activity",
      startDate: "2022-08-08",
    },
  });

  const { handleSubmit } = form;

  return (
    <WrapperForm methods={form}>
      <ActivityConfiguration
        {...args}
        minStartDate={minStartDate}
        maxEndDate={maxEndDate}
      />
      <ButtonPrimary
        className="mt-4"
        onClick={handleSubmit(action("onSubmit"))}
        label="Submit"
      />
    </WrapperForm>
  );
};

export const Playground = Template.bind({});

export const WithActivityAttributes = Template.bind({});
WithActivityAttributes.args = {
  activityTypeLibrary,
};
