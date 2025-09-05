import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import CrewInformation from "./CrewInformation";

export default {
  title: "Container/Report/Crew/Information",
  component: CrewInformation,
} as ComponentMeta<typeof CrewInformation>;

const DUMMY_COMPANIES = [
  { id: 1, name: "Urbint" },
  { id: 2, name: "Microsoft" },
  { id: 3, name: "Tesla" },
  { id: 4, name: "Amazon" },
] as unknown as InputSelectOption[];

const Template: ComponentStory<typeof CrewInformation> = () => {
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
      <CrewInformation companies={DUMMY_COMPANIES} />
    </WrapperForm>
  );
};

export const Playground = Template.bind({});
