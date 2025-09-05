import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Activity } from "@/types/activity/Activity";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import { Activities } from "./Activities";

const dummyActivities: Activity[] = [
  {
    id: "1",
    name: "Test Activity",
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.NOT_STARTED,
    taskCount: 1,
    tasks: [
      {
        id: "1",
        name: "Pipe Face Alignment",
        riskLevel: RiskLevel.MEDIUM,
        activity: {} as Activity,
        hazards: [
          {
            id: "1",
            name: "Pinch Point",
            isApplicable: true,
            controls: [
              {
                id: "1",
                name: "Gloves",
                isApplicable: true,
              },
              {
                id: "2",
                name: "Situational Jobsite Awareness",
                isApplicable: true,
              },
            ],
          },
        ],
        incidents: [],
      },
    ],
  },
  {
    id: "2",
    name: "Second Activity",
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.IN_PROGRESS,
    taskCount: 1,
    tasks: [
      {
        id: "7",
        name: "Grinding",
        riskLevel: RiskLevel.MEDIUM,
        activity: {} as Activity,
        hazards: [
          {
            id: "1",
            name: "Pinch Point",
            isApplicable: true,
            controls: [
              {
                id: "1",
                name: "Test Control",
                isApplicable: true,
              },
              {
                id: "2",
                name: "Situational Jobsite Awareness",
                isApplicable: true,
              },
            ],
          },
        ],
        incidents: [],
      },
    ],
  },
];

export default {
  title: "Container/SummaryView/LocationDetails/Activities",
  component: Activities,
  decorators: [
    Story => (
      <div className="w-full md:w-[500px] h-[800px]">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Activities>;

const Template: ComponentStory<typeof Activities> = args => (
  <Activities {...args} />
);

export const WithTaskCardsOpen = Template.bind({});

WithTaskCardsOpen.args = {
  elements: dummyActivities,
  isCardOpen: () => true,
};

export const WithTaskCardsClosed = Template.bind({});

WithTaskCardsClosed.args = {
  elements: dummyActivities,
  isCardOpen: () => false,
};
