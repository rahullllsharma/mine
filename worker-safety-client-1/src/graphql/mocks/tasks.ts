import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";

export const tasks = [
  {
    id: "task1",
    name: "Loading/Unloading",
    riskLevel: RiskLevel.MEDIUM,
    activity: {
      id: "activity1",
      name: "activity1",
      startDate: "2021-10-10",
      endDate: "2021-10-11",
      status: TaskStatus.NOT_STARTED,
      taskCount: 2,
    },
    hazards: [
      {
        id: "task1_hazard1",
        isApplicable: true,
        name: "Struck by Pipe/Pinch Points",
        controls: [
          {
            id: "task1_hazard1_control1",
            name: "Situational Jobsite Awareness",
            isApplicable: true,
          },
        ],
      },
      {
        id: "task1_hazard2",
        isApplicable: true,
        name: "Struck by Moving Vehicle",
        controls: [
          {
            id: "task1_hazard2_control1",
            name: "Situational Jobsite Awareness",
            isApplicable: true,
          },
          {
            id: "task1_hazard2_control2",
            name: "Exclusion Zone",
            isApplicable: true,
          },
        ],
      },
    ],
  },
  {
    id: "task2",
    name: "Pipe Face Alignment",
    riskLevel: RiskLevel.MEDIUM,
    activity: {
      id: "activity1",
      name: "activity1",
      startDate: "2021-10-10",
      endDate: "2021-10-11",
      status: TaskStatus.NOT_STARTED,
      taskCount: 2,
    },
    hazards: [
      {
        id: "task2_hazard1",
        isApplicable: true,
        name: "Pinch Points",
        controls: [
          {
            id: "task2_hazard1_control1",
            name: "Gloves",
            isApplicable: true,
          },
          {
            id: "task2_hazard1_control2",
            name: "Situational Jobsite Awareness",
            isApplicable: true,
          },
        ],
      },
      {
        id: "task2_hazard2",
        isApplicable: true,
        name: "Struck by Equipment and Material",
        controls: [
          {
            id: "task2_hazard2_control1",
            name: "Gloves",
            isApplicable: true,
          },
          {
            id: "task2_hazard2_control2",
            name: "Situational Jobsite Awareness",
            isApplicable: true,
          },
        ],
      },
    ],
  },
];
