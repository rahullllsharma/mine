import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";

export const siteConditions = [
  {
    id: "site1",
    name: "High Heat Index",
    riskLevel: RiskLevel.HIGH,
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.NOT_STARTED,
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
  },
  {
    id: "site2",
    name: "High Traffic Density",
    riskLevel: RiskLevel.HIGH,
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.NOT_STARTED,
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
  },
];
