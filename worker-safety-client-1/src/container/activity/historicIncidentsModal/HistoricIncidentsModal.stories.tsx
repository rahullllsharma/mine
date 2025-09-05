import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { HistoricIncidentsModal } from "./HistoricIncidentsModal";

const taskWithIncidents = {
  id: "1",
  hazards: [],
  incidents: [
    {
      id: "590087",
      description:
        "Kiewit (contractor) electrician was moving a pipe threading machine and felt a tweak in their lower back. The employee stopped work and reported to field safety. First aid was provided onsite and then the employee returned to work.",
      incidentDate: "2021-10-28T09:32:20.464954",
      incidentType: "Injury/Illness",
      severity: "first_aid",
    },
    {
      id: "590695",
      description:
        "The employee was picking up parts and loading them into the truck. While strapping the parts down, the employee stepped up on the side of the truck, lost their balance, and fell to the ground. The employee broke several ribs and punctured their lung.",
      incidentDate: "2021-11-29T09:32:20.464954",
      incidentType: "Injury/Illness",
      severity: "lost_time",
    },
    {
      id: "585759",
      description:
        "Contractor electrician (Kiewit) came to work with discomfort in their back. The electrician was not able to perform their job duties and left the worksite. This was a pre-existing non-work related condition.",
      incidentDate: "2021-04-29T09:32:20.464954",
      incidentType: "Injury/Illness",
      severity: "p_sif",
    },
  ],
  name: "Task name",
  riskLevel: RiskLevel.UNKNOWN,
};
const taskWithoutIncidents = {
  id: "1",
  hazards: [],
  incidents: [],
  name: "Task name",
  riskLevel: RiskLevel.UNKNOWN,
};

export default {
  title: "Layout/Modals/HistoricIncidentsModal",
  component: HistoricIncidentsModal,
  argTypes: {
    onModalClose: { action: "onModalCloseClicked" },
  },
} as ComponentMeta<typeof HistoricIncidentsModal>;

const Template: ComponentStory<typeof HistoricIncidentsModal> = args => (
  <HistoricIncidentsModal {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  task: taskWithIncidents as TaskHazardAggregator,
};

export const WithoutIncidents = Template.bind({});
WithoutIncidents.args = {
  task: taskWithoutIncidents,
};
