import type { LocationDetailsProp } from "./LocationDetails";
import { render, screen } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import { TaskStatus } from "@/types/task/TaskStatus";
import {
  mockIntlDateTimeFormatLocale,
  mockTenantStore,
} from "@/utils/dev/jest";
import { LocationDetails } from "./LocationDetails";

const props = {
  onTaskClick: jest.fn(),
  onAddTask: jest.fn(),
  onSiteConditionClick: jest.fn(),
  onAddSiteCondition: jest.fn(),
  onDailyReportClick: jest.fn(),
  onAddDailyReport: jest.fn(),
  onAddActivity: jest.fn(),
  projectId: "",
  startDate: "",
  projectStartDate: "",
  projectEndDate: "",
  location: {
    id: "1",
    name: "Location name",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "El",
    },
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions: [
      {
        id: "1",
        name: "High Heat Index",
        riskLevel: RiskLevel.MEDIUM,
        startDate: "2021-10-10",
        endDate: "2021-10-11",
        isManuallyAdded: true,
        supervisor: {
          id: "1",
          name: "El",
        },
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
        },
        status: TaskStatus.NOT_STARTED,
        hazards: [
          {
            id: "1",
            name: "Dehydration",
            isApplicable: true,
            controls: [
              {
                id: "1",
                name: "Replenish Water Supply",
                isApplicable: true,
              },
            ],
          },
        ],
        createdBy: {
          id: "111",
          name: "El",
        },
        incidents: [],
      },
    ],
    tasks: [
      {
        id: "1",
        name: "Pipe Face Alignment",
        riskLevel: RiskLevel.MEDIUM,
        startDate: "2021-10-10",
        endDate: "2021-10-11",
        status: TaskStatus.NOT_STARTED,
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
    activities: [],
    dailyReports: [
      {
        id: "6162b039-40ad-486f-b6f7-2efb3822c437",
        createdBy: {
          id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
          name: "Test User",
        },
        createdAt: "2022-02-02T09:32:20.464954",
        status: DailyReportStatus.IN_PROGRESS,
      },
      {
        id: "6162b039-40ad-486f-b6f7-2efb3822c438",
        createdBy: {
          id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
          name: "Test User",
        },
        createdAt: "2022-02-02T09:32:20.464954",
        completedBy: {
          id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
          name: "Test User",
        },
        completedAt: "2022-02-02T09:32:20.464954",
        status: DailyReportStatus.COMPLETE,
      },
    ],
    jobSafetyBriefings: [],
  },
};

describe(LocationDetails.name, () => {
  beforeAll(() => {
    mockTenantStore();
    mockIntlDateTimeFormatLocale("en-gb");
  });

  it("should render correctly", () => {
    const { asFragment } = render(<LocationDetails {...props} />);
    expect(asFragment()).toMatchSnapshot();
  });

  describe("Activity section", () => {
    it("should render activities in a list", () => {
      const locationPropsWithActivities = {
        ...props,
        location: {
          ...props.location,
          activities: [
            {
              id: "Activity 1",
              name: "Activity 1",
              status: TaskStatus.IN_PROGRESS,
              startDate: "2022-01-01",
              endDate: "2022-01-31",
              tasks: [
                {
                  id: "task 1",
                  name: "task 1",
                  hazards: [],
                },
              ],
            },
            {
              id: "Activity 2",
              name: "Activity 2",
              status: TaskStatus.IN_PROGRESS,
              startDate: "2022-01-01",
              endDate: "2022-01-31",
              tasks: [
                {
                  id: "task",
                  name: "task",
                  hazards: [],
                },
              ],
            },
            {
              id: "Activity 3",
              name: "Activity 3",
              status: TaskStatus.IN_PROGRESS,
              startDate: "2022-01-01",
              endDate: "2022-01-31",
              tasks: [
                {
                  id: "task 1",
                  name: "task 1",
                  hazards: [],
                },
                {
                  id: "task 2",
                  name: "task 2",
                  hazards: [],
                },
              ],
            },
          ],
        },
      } as unknown as LocationDetailsProp;

      render(
        <MockedProvider>
          <LocationDetails {...locationPropsWithActivities} />
        </MockedProvider>
      );

      expect(
        screen.getByRole("heading", {
          name: /activities \(3\)/i,
        })
      ).toBeInTheDocument();

      screen.getByText(/activity 1/gi);
      screen.getByText(/activity 2/gi);
      screen.getByText(/activity 3/gi);
    });
  });
});
