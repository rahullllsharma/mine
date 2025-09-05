import type { Activity } from "@/types/activity/Activity";
import { render, screen } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import { mockTenantStore } from "@/utils/dev/jest";
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
        activity: {} as Activity,
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
        activity: {} as Activity,
      },
    ],
  },
];

describe(Activities.name, () => {
  beforeAll(() => {
    mockTenantStore();
  });
  const props = {
    elements: dummyActivities,
    onElementClick: jest.fn(),
    projectStartDate: "",
    projectEndDate: "",
    isCardOpen: jest.fn(),
    onCardToggle: jest.fn(),
  };

  it("should render the component correctly", () => {
    const { asFragment } = render(
      <MockedProvider>
        <Activities {...props} />
      </MockedProvider>
    );
    expect(asFragment()).toMatchSnapshot();
    dummyActivities.forEach(activity => {
      expect(screen.getByText(activity.name)).toBeInTheDocument();
    });
  });
});
