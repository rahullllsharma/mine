import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import CrewMembers from "./CrewMembers";

export default {
  title: "Container/Report/Crew/Members",
  component: CrewMembers,
} as ComponentMeta<typeof CrewMembers>;

const Template: ComponentStory<typeof CrewMembers> = () => {
  const methods = useForm<DailyReportInputs>({
    defaultValues: {
      crew: {
        nWelders: "",
        nSafetyProf: "",
        nOperators: "",
        nFlaggers: "",
        nLaborers: "",
        nOtherCrew: "",
      },
    },
  });
  return (
    <WrapperForm methods={methods}>
      <CrewMembers />
    </WrapperForm>
  );
};

export const Playground = Template.bind({});
