import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { MultiStepFormProps } from "./MultiStepForm";
import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import { useState } from "react";
import { action } from "@storybook/addon-actions";

import { useProjects } from "@/hooks/useProjects";
import WorkSchedule from "../workSchedule/WorkSchedule";
import Tasks from "../tasks/Tasks";
import JobHazardAnalysis from "../jobHazardAnalysis/JobHazardAnalysis";
import Crew from "../crew/Crew";
import AdditionalInformation from "../additionalInformation/AdditionalInformation";
import SafetyAndCompliance from "../safetyAndCompliance/SafetyAndCompliance";
import MultiStepForm from "./MultiStepForm";

const DUMMY_COMPANIES = [
  { id: 1, name: "Urbint" },
  { id: 2, name: "Microsoft" },
  { id: 3, name: "Tesla" },
  { id: 4, name: "Amazon" },
] as unknown as InputSelectOption[];

type StoryProps = MultiStepFormProps & { withSubmit?: boolean };

// eslint-disable-next-line react-hooks/rules-of-hooks
const project = useProjects()[0];
const [location] = project.locations;

export default {
  title: "Container/Report/MultiStepForm",
  component: MultiStepForm,
  decorators: [
    Story => (
      <div className="overflow-scroll w-full pb-5 max-h-screen">
        <Story />
      </div>
    ),
  ],
  story: {
    parameters: {
      nextRouter: {
        asPath: "/",
        push: function (path: string) {
          this.asPath = path;
          action(`router: push ${this.asPath}`)();
        },
      },
    },
  },
} as ComponentMeta<typeof MultiStepForm>;

const metadata = [
  {
    id: "work-schedule",
    name: "Work Schedule",
    path: "#work-schedule",
    Component: WorkSchedule,
  },
  {
    id: "tasks",
    name: "Tasks",
    path: "#tasks",
    Component: Tasks,
  },
  {
    id: "job-hazard-analysis",
    name: "Job Hazard Analysis",
    path: "#job-hazard-analysis",
    Component: function JobHazardAnalysisSection() {
      const { siteConditions, tasks } = location;
      return (
        <JobHazardAnalysis tasks={tasks} siteConditions={siteConditions} />
      );
    },
  },
  {
    id: "safety-and-compliance",
    name: "Safety And Compliance",
    path: "#safety-and-compliance",
    Component: SafetyAndCompliance,
  },
  {
    id: "crew",
    name: "Crew",
    path: "#crew",
    Component: function CrewSection() {
      return <Crew companies={DUMMY_COMPANIES} />;
    },
  },
  {
    id: "additional-information",
    name: "Additional Information",
    path: "#additional-information",
    Component: AdditionalInformation,
  },
];

const Template: ComponentStory<typeof MultiStepForm> = (args: StoryProps) => {
  const [state, setState] = useState({});

  return (
    <>
      <pre>current {JSON.stringify(state)}</pre>
      <MultiStepForm
        // FIXME: we don't need a debug mode in the future
        UNSAFE_WILL_BE_REMOVED_debugMode={args.UNSAFE_WILL_BE_REMOVED_debugMode}
        steps={metadata}
        onComplete={data => {
          console.log("🏁 multi step: onComplete", data);
          setState(prev => ({
            ...prev,
            data,
          }));
        }}
        onStepMount={() => {
          console.log("⛳️ multi step: on step MOUNT");
          return {
            startDate: "2022-02-15",
            endDate: "2022-02-17",
            dateLimits: {
              projectStartDate: project.startDate,
              projectEndDate: project.endDate,
            },
            tasks: location.tasks,
          };
        }}
        onStepUnmount={formData => {
          const data = (formData || {}) as unknown as Record<string, unknown>;
          console.log("🛑 multi step: on step UNMOUNT", data, state);
          setState(prev => ({
            ...prev,
            ...data,
          }));
        }}
        onStepChange={data => {
          console.log("🚶 multi step: on step CHANGE", data);
        }}
        onStepSave={formData => {
          const data = (formData || {}) as unknown as Record<string, unknown>;
          console.log("💾 multi step: on step SAVE", data);

          setState(prevState => ({
            ...prevState,
            ...data,
          }));

          return Promise.resolve(true);
        }}
      />
    </>
  );
};

export const Default = Template.bind({});
Default.args = {};
