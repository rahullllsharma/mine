import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import type { SiteConditionInputs } from "@/types/siteCondition/SiteConditionInputs";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import SiteConditionDetailsForm from "./SiteConditionDetailsForm";

export default {
  title: "Components/SiteCondition/Details/SiteConditionDetails",
  component: SiteConditionDetailsForm,
} as ComponentMeta<typeof SiteConditionDetailsForm>;

const TemplateSiteConditionDetails: ComponentStory<
  typeof SiteConditionDetailsForm
> = ({ siteCondition, ...tailProps }) => {
  const form = useForm<SiteConditionInputs>({
    defaultValues: {
      librarySiteConditionId: siteCondition.id,
    },
  });

  const { handleSubmit } = form;

  return (
    <div className="h-screen px-1 pb-8 overflow-auto">
      <WrapperForm methods={form}>
        <ButtonPrimary
          onClick={handleSubmit(action("onSubmit"))}
          label="Submit"
        />
        <SiteConditionDetailsForm
          siteCondition={siteCondition}
          {...tailProps}
        />
      </WrapperForm>
    </div>
  );
};

export const SiteCondition = TemplateSiteConditionDetails.bind({});

const controlsLibrary: Control[] = [
  { id: "custom-control-1", name: "Control 1", isApplicable: true },
  { id: "custom-control-2", name: "Control 2", isApplicable: true },
  { id: "custom-control-3", name: "Control 3", isApplicable: true },
  { id: "custom-control-4", name: "Control 4", isApplicable: true },
];

// Information should be retrieved by using useQuery and fetched from BE
const hazardsLibrary: Hazard[] = [
  { id: "custom-hazard-1", name: "Hazard 1", isApplicable: true, controls: [] },
  { id: "custom-hazard-2", name: "Hazard 2", isApplicable: true, controls: [] },
  { id: "custom-hazard-3", name: "Hazard 3", isApplicable: true, controls: [] },
  { id: "custom-hazard-4", name: "Hazard 4", isApplicable: true, controls: [] },
];
const sharedArgs = {
  siteCondition: {
    id: "1",
    name: "Site Condition 1",
    isManuallyAdded: false,
    hazards: [
      {
        id: "1",
        name: "hazard 123",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "2",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
      {
        id: "2",
        name: "hazard 567",
        isApplicable: true,
        controls: [
          {
            id: "12",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "22",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
    ],
    incidents: [],
  },
  hazardsLibrary,
  controlsLibrary,
};

SiteCondition.args = sharedArgs;

export const SiteConditionWithManualHazardsAndControl =
  TemplateSiteConditionDetails.bind({});

SiteConditionWithManualHazardsAndControl.args = {
  siteCondition: {
    ...sharedArgs.siteCondition,
    hazards: [
      {
        id: "custom-hazard-2",
        name: "Hazard 2",
        isApplicable: true,
        createdBy: {
          id: "0",
          name: "User",
        },
        controls: [],
      },
      {
        id: "custom-hazard-4",
        name: "Hazard 4",
        isApplicable: true,
        createdBy: {
          id: "0",
          name: "User",
        },
        controls: [],
      },
      {
        id: "h-1",
        name: "Bodily Injury",
        isApplicable: true,
        controls: [
          {
            id: "c-1",
            name: "Situational Jobsite Awareness",
            isApplicable: false,
          },
          {
            id: "c-2",
            name: "Trained and Qualified",
            isApplicable: true,
          },
        ],
      },
      {
        id: "h-2",
        name: "Radiation Sickness",
        isApplicable: true,
        controls: [
          {
            id: "c-3",
            name: "Radiation Monitoring Device",
            isApplicable: true,
          },
          {
            id: "c-4",
            name: "Isotopes Stored and Handled Properly",
            isApplicable: true,
          },
        ],
      },
    ],
  },
  hazardsLibrary: sharedArgs.hazardsLibrary,
  controlsLibrary: sharedArgs.controlsLibrary,
};
