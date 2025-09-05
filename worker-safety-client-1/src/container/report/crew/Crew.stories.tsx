import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Crew from "./Crew";

export default {
  title: "Container/Report/Crew",
  component: Crew,
} as ComponentMeta<typeof Crew>;

const DUMMY_COMPANIES = [
  { id: 1, name: "Urbint" },
  { id: 2, name: "Microsoft" },
  { id: 3, name: "Tesla" },
  { id: 4, name: "Amazon" },
] as unknown as InputSelectOption[];

const Template: ComponentStory<typeof Crew> = args => (
  <div className="overflow-auto p-2 pb-10" style={{ height: "90vh" }}>
    <Crew {...args} />
  </div>
);

const defaultValues: DailyReportInputs = {
  crew: {
    contractor: "",
    foremanName: "",
    nWelders: "",
    nSafetyProf: "",
    nOperators: "",
    nFlaggers: "",
    nLaborers: "",
    nOtherCrew: "",
    documents: [],
  },
};

export const WithoutSubmit = (): JSX.Element => (
  <WrapperForm>
    <Template companies={DUMMY_COMPANIES} />
  </WrapperForm>
);

export const WithSubmit = (): JSX.Element => {
  const methods = useForm<DailyReportInputs>({
    defaultValues,
  });
  return (
    <WrapperForm methods={methods}>
      <ButtonPrimary
        className="mb-4"
        onClick={methods.handleSubmit(action("onSubmit"))}
        label="Submit"
      />
      <Template companies={DUMMY_COMPANIES} />
    </WrapperForm>
  );
};

export const Readonly = (): JSX.Element => {
  const methods = useForm<DailyReportInputs>({
    defaultValues: {
      crew: {
        contractor: DUMMY_COMPANIES[0].name,
        foremanName: "Joe Smith",
        nWelders: 1,
        nSafetyProf: 2,
        nOperators: 3,
        nFlaggers: 4,
        nLaborers: 5,
        nOtherCrew: 6,
        // documents: [
        //   {
        //     id: nanoid(),
        //     name: "Document 1.txt",
        //     displayName: "Document 1.txt",
        //     size: "518 KB",
        //     date: convertDateToString(new Date()),
        //     time: "10:30",
        //   },
        // ],
      },
    },
  });
  return (
    <WrapperForm methods={methods}>
      <Template companies={DUMMY_COMPANIES} isCompleted />
    </WrapperForm>
  );
};
