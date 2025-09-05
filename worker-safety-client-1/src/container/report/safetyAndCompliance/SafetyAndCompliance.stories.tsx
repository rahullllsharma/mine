import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import SafetyAndCompliance from "./SafetyAndCompliance";

export default {
  title: "Container/Report/SafetyAndCompliance",
  component: SafetyAndCompliance,
  decorators: [
    Story => (
      <div className="max-w-lg overflow-auto p-6 h-screen">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof SafetyAndCompliance>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "", membersReviewedAndSignedOff: "" },
    jobBrief: {
      comprehensiveJobBriefConduct: "",
      comprehensiveJobBriefConductNotes: "",
      jobBriefConductAfterWork: "",
      jobBriefConductAfterWorkNotes: "",
    },
    workMethods: { contractorAccess: "", contractorAccessNotes: "" },
    digSafeMarkOuts: {
      markOutsVerified: "",
      markOutsVerifiedNotes: "",
      facilitiesLocatedAndExposed: "",
      facilitiesLocatedAndExposedNotes: "",
      digSafeMarkOutsLocation: "",
    },
    systemOperatingProcedures: {
      onSiteAndCurrent: "",
      onSiteAndCurrentNotes: "",
      gasControlsNotified: "",
      gasControlsNotifiedNotes: "",
      sopId: "",
      sopType: "",
      sopStepsCalledIn: "",
      sopComments: "",
    },
    spottersSafetyObserver: {
      safetyObserverAssigned: "",
      safetyObserverAssignedNotes: "",
      spotterIdentifiedMachineryBackingUp: "",
    },
    privateProtectionEquipment: {
      wearingPPE: "",
      wearingPPENotes: "",
    },
    operatorQualifications: {
      qualificationsVerified: "",
      qualificationsVerifiedNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "1", membersReviewedAndSignedOff: "1" },
    jobBrief: {
      comprehensiveJobBriefConduct: "1",
      comprehensiveJobBriefConductNotes: "Conducts notes",
      jobBriefConductAfterWork: "-1",
      jobBriefConductAfterWorkNotes: "After work notes",
    },
    workMethods: {
      contractorAccess: "0",
      contractorAccessNotes: "Not granted",
    },
    digSafeMarkOuts: {
      markOutsVerified: "-1",
      markOutsVerifiedNotes: "N/A",
      facilitiesLocatedAndExposed: "1",
      facilitiesLocatedAndExposedNotes: "Yes",
      digSafeMarkOutsLocation: "No additional notes",
    },
    systemOperatingProcedures: {
      onSiteAndCurrent: "0",
      onSiteAndCurrentNotes: "On-site and current notes",
      gasControlsNotified: "1",
      gasControlsNotifiedNotes: "Gas control notification notes",
      sopId: "#11AA22",
      sopType: "Unknown",
      sopStepsCalledIn: "Steps called in",
      sopComments: "No additional comments",
    },
    spottersSafetyObserver: {
      safetyObserverAssigned: "0",
      safetyObserverAssignedNotes: "Not yet",
      spotterIdentifiedMachineryBackingUp: "1",
    },
    privateProtectionEquipment: {
      wearingPPE: "0",
      wearingPPENotes:
        "No security/protection measures applied to any crew member nor visitors",
    },
    operatorQualifications: {
      qualificationsVerified: "1",
      qualificationsVerifiedNotes: "All ok",
    },
  },
};

const Template: ComponentStory<typeof SafetyAndCompliance> = args => (
  <SafetyAndCompliance {...args} />
);

const WithSubmitButton = (defaultValues: DailyReportInputs): JSX.Element => {
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
      <Template />
    </WrapperForm>
  );
};

export const WithoutSubmit = (): JSX.Element => (
  <WrapperForm>
    <Template />
  </WrapperForm>
);

export const WithSubmitEmpty = (): JSX.Element => {
  return <WithSubmitButton {...emptyStateValues} />;
};

export const WithSubmitFilled = (): JSX.Element => {
  return <WithSubmitButton {...prefilledValues} />;
};

export const Readonly = (): JSX.Element => {
  const methods = useForm<DailyReportInputs>({
    defaultValues: prefilledValues,
  });
  return (
    <WrapperForm methods={methods}>
      <Template isCompleted />
    </WrapperForm>
  );
};
