import type { Project } from "../types/project/Project";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import { RiskLevel } from "../components/riskBadge/RiskLevel";
import { TaskStatus } from "../types/task/TaskStatus";

const projects: Project[] = [
  {
    id: "7114445f-966a-42e2-aa3b-0e4d5365075d",
    name: "5th Street Main Relocation",
    riskLevel: RiskLevel.HIGH,
    supervisor: { id: "2", name: "Jakob Aminoff" },
    manager: { id: "1", name: "Jakob Aminoff" },
    additionalSupervisors: [
      { id: "3", name: "Sirius Goldberg" },
      { id: "4", name: "Hailey Quinn" },
    ],
    contractor: { id: "1", name: "Jakob Aminoff" },
    region: "Northeast",
    status: "ACTIVE",
    libraryProjectType: { id: "1", name: "Main replacement" },
    libraryDivision: { id: "1", name: "Gas" },
    libraryRegion: { id: "1", name: "NE (New England)" },
    startDate: "2021-12-28",
    endDate: "2022-12-31",
    externalKey: "123",
    contractReference: "AAA",
    libraryAssetType: {
      id: "1",
      name: "Global Application",
    },
    contractName: "some name",
    projectZipCode: "84847-323",
    engineerName: "Paul Engineer",
    locations: [
      {
        id: "1",
        name: "Park Avenue",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [
          {
            id: "site1",
            name: "High Heat Index",
            riskLevel: RiskLevel.HIGH,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
            isManuallyAdded: false,
            hazards: [
              {
                id: "site1_hazard1",
                isApplicable: true,
                name: "Dehydration",
                controls: [
                  {
                    id: "site1_hazard1_control1",
                    name: "Replenish Water Supply",
                    isApplicable: true,
                  },
                ],
              },
            ],
            incidents: [],
          },
          {
            id: "site2",
            name: "High Traffic Density",
            riskLevel: RiskLevel.HIGH,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
            isManuallyAdded: false,
            hazards: [
              {
                id: "site2_hazard1",
                isApplicable: true,
                name: "Getting Struck by Moving Vehicles",
                controls: [
                  {
                    id: "site2_hazard1_control1",
                    name: "Traffic Control Devices & a spotter",
                    isApplicable: true,
                  },
                ],
              },
            ],
            incidents: [],
          },
        ],
        tasks: [
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
              tasks: [],
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
            incidents: [],
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
              tasks: [],
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
      {
        id: "2",
        name: "E 96th St",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [
          {
            id: "2",
            name: "High Traffic Density",
            riskLevel: RiskLevel.LOW,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
            isManuallyAdded: false,
            hazards: [
              {
                id: "1",
                name: "Getting Struck by Moving Vehicles",
                isApplicable: true,
                controls: [
                  {
                    id: "1",
                    name: "Traffic control devices & a spotter",
                    isApplicable: true,
                  },
                ],
              },
            ],
            incidents: [],
          },
        ],
        tasks: [
          {
            id: "1",
            name: "Pipe Face Alignment",
            riskLevel: RiskLevel.MEDIUM,
            activity: {
              id: "activity1",
              name: "activity1",
              startDate: "2021-10-10",
              endDate: "2021-10-11",
              status: TaskStatus.NOT_STARTED,
              taskCount: 1,
              tasks: [],
            },
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
      {
        id: "3",
        name: "E 97th St",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [],
        tasks: [],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
      {
        id: "4",
        name: "E 98th St",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [],
        tasks: [],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
    ],
  },
  {
    id: "7114445f-966a-42e2-aa3b-0e4d53650751a",
    name: "N. Washington Street Bridge",
    riskLevel: RiskLevel.LOW,
    supervisor: { id: "1", name: "Jakob Aminoff" },
    manager: { id: "1", name: "Jakob Aminoff" },
    additionalSupervisors: [
      { id: "234", name: "Raymond Holt" },
      { id: "235", name: "Sirius Goldberg" },
      { id: "236", name: "Hailey Quinn" },
    ],
    contractor: { id: "1", name: "Jakob Aminoff" },
    region: "Northeast",
    status: "Active",
    libraryProjectType: { id: "1", name: "Bridge replacement" },
    libraryDivision: { id: "1", name: "Gas" },
    libraryRegion: { id: "1", name: "NE (New England)" },
    startDate: "2021-12-28",
    endDate: "2022-12-31",
    externalKey: "123",
    contractReference: "AAA",
    libraryAssetType: {
      id: "1",
      name: "Global Application",
    },
    contractName: "some name",
    projectZipCode: "84847-323",
    engineerName: "Paul Engineer",
    locations: [
      {
        id: "1",
        name: "Location 1",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
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
            name: "Site 1",
            riskLevel: RiskLevel.HIGH,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
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
            ],
            incidents: [],
          },
          {
            id: "2",
            name: "Site 2",
            riskLevel: RiskLevel.LOW,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
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
            ],
            incidents: [],
          },
        ],
        tasks: [
          {
            id: "1",
            name: "Task 1",
            riskLevel: RiskLevel.MEDIUM,
            activity: {
              id: "activity1",
              name: "activity1",
              startDate: "2021-10-10",
              endDate: "2021-10-11",
              status: TaskStatus.NOT_STARTED,
              taskCount: 1,
              tasks: [],
            },
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
            ],
            incidents: [],
          },
        ],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
      {
        id: "2",
        name: "Location 2",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
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
            name: "Site 123",
            riskLevel: RiskLevel.HIGH,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
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
            ],
            incidents: [],
          },
          {
            id: "2",
            name: "Site 456",
            riskLevel: RiskLevel.LOW,
            startDate: "2021-10-10",
            endDate: "2021-10-11",
            status: TaskStatus.NOT_STARTED,
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
            ],
            incidents: [],
          },
        ],
        tasks: [
          {
            id: "1",
            name: "Task 1",
            riskLevel: RiskLevel.MEDIUM,
            activity: {
              id: "activity1",
              name: "activity1",
              startDate: "2021-10-10",
              endDate: "2021-10-11",
              status: TaskStatus.NOT_STARTED,
              taskCount: 1,
              tasks: [],
            },
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
            ],
            incidents: [],
          },
        ],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
      {
        id: "3",
        name: "Location 3",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [],
        tasks: [],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
      {
        id: "4",
        name: "Location 4",
        latitude: 34.054913,
        longitude: -62.136754,
        supervisor: { id: "1", name: "Jakob Aminoff" },
        additionalSupervisors: [
          { id: "235", name: "Sirius Goldberg" },
          { id: "236", name: "Hailey Quinn" },
        ],
        riskLevel: RiskLevel.MEDIUM,
        riskCalculation: {
          totalTaskRiskLevel: RiskLevel.UNKNOWN,
          isSupervisorAtRisk: false,
          isContractorAtRisk: false,
          isCrewAtRisk: false,
        },
        siteConditions: [],
        tasks: [],
        activities: [],
        dailyReports: [],
        jobSafetyBriefings: [],
      },
    ],
  },
];

export function useProjects(): Project[] {
  return projects;
}
