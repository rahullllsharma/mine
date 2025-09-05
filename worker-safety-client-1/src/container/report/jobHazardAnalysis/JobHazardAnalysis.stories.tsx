import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { JobHazardAnalysisProps } from "./JobHazardAnalysis";
import type { JobHazardAnalysisGraphQLPayloadParams } from "./transformers/graphQLPayload";
import type {
  JobHazardAnalysisSectionInputs,
  SiteConditionAnalysisInputs,
  TaskAnalysisInputs,
} from "@/types/report/DailyReportInputs";
import { FormProvider, useForm } from "react-hook-form";
import { DevTool } from "@hookform/devtools";
import { action } from "@storybook/addon-actions";

import { tasks } from "@/graphql/mocks/tasks";
import { siteConditions } from "@/graphql/mocks/siteConditions";
import JobHazardAnalysis from "./JobHazardAnalysis";
import graphQLPayload from "./transformers/graphQLPayload";

export default {
  title: "Container/Report/JobHazardAnalysis",
  component: JobHazardAnalysis,
} as ComponentMeta<typeof JobHazardAnalysis>;

const Template = ({
  withSubmit,
  ...args
}: JobHazardAnalysisProps & { withSubmit?: boolean }) => {
  const methods = useForm();
  const onSubmit = (formData: JobHazardAnalysisGraphQLPayloadParams) => {
    console.log("formData = ", JSON.stringify(formData));
    console.log(
      "graphQLPayload(formData) =",
      JSON.stringify(graphQLPayload(formData))
    );
    action("on submit")(formData);
  };

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={methods.handleSubmit(onSubmit)}
        className="max-w-lg overflow-auto p-1"
        style={{ height: "90vh" }}
      >
        <JobHazardAnalysis
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          tasks={tasks}
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          siteConditions={siteConditions}
          {...args}
        />
        {withSubmit && (
          <>
            <input type="submit" />
            <DevTool control={methods.control} />
          </>
        )}
      </form>
    </FormProvider>
  );
};

export const Playground = Template.bind({});

export const Readonly: ComponentStory<typeof JobHazardAnalysis> = args => {
  const defaultValues = {
    siteConditions: [
      {
        id: "site1",
        isApplicable: true,
        hazards: [
          {
            id: "site1_hazard1",
            isApplicable: true,
            controls: [
              {
                id: "site1_hazard1_control1",
                implemented: false,
                notImplementedReason: "Other controls in place",
              },
            ],
          },
        ],
      },
      {
        id: "site2",
        isApplicable: false,
        hazards: [
          {
            id: "site2_hazard1",
            isApplicable: true,
            controls: [
              {
                id: "site2_hazard1_control1",
                implemented: true,
              },
            ],
          },
        ],
      },
    ] as unknown as SiteConditionAnalysisInputs,
    tasks: [
      {
        id: "task1",
        performed: false,
        notes: "hello from default",
        notApplicableReason: "Contractor Delay",
        hazards: [],
      },
      {
        id: "task2",
        performed: true,
        notes: "hello from default",
        hazards: [
          {
            id: "task2_hazard1",
            isApplicable: false,
            controls: [],
          },
          {
            id: "task2_hazard2",
            isApplicable: true,
            controls: [
              {
                id: "task2_hazard2_control1",
                implemented: true,
              },
              {
                id: "task2_hazard2_control2",
                implemented: false,
                notImplementedReason: "Other controls in place",
              },
            ],
          },
        ],
      },
    ] as unknown as TaskAnalysisInputs,
  } as unknown as JobHazardAnalysisSectionInputs;
  return (
    <>
      <Template isCompleted {...args} defaultValues={defaultValues} />
    </>
  );
};

export const WithSubmit: ComponentStory<typeof JobHazardAnalysis> = args => {
  return (
    <>
      <Template {...args} withSubmit />
    </>
  );
};

export const WithDefaultValues: ComponentStory<typeof JobHazardAnalysis> =
  args => {
    const defaultValues = {
      siteConditions: [
        {
          id: "site1",
          isApplicable: true,
          hazards: [
            {
              id: "site1_hazard1",
              isApplicable: true,
              controls: [
                {
                  id: "site1_hazard1_control1",
                  implemented: false,
                  notImplementedReason: "Other controls in place",
                },
              ],
            },
          ],
        },
      ] as unknown as SiteConditionAnalysisInputs,
      tasks: [
        {
          id: "task1",
          performed: false,
          notes: "hello from default",
          notApplicableReason: "Contractor Delay",
          hazards: [
            {
              id: "task1_hazard1",
              isApplicable: false,
              controls: [
                {
                  id: "task1_hazard1_control1",
                  implemented: true,
                },
                {
                  id: "task1_hazard1_control2",
                  implemented: false,
                },
              ],
            },
          ],
        },
      ] as unknown as TaskAnalysisInputs,
    } as unknown as JobHazardAnalysisSectionInputs;
    return <Template {...args} defaultValues={defaultValues} withSubmit />;
  };

export const WithEmptyState: ComponentStory<typeof JobHazardAnalysis> =
  args => {
    return <Template {...args} tasks={[]} siteConditions={[]} />;
  };
