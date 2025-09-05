import { render, screen } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import JobHazardAnalysis from "./JobHazardAnalysis";

const siteConditions = [
  {
    hazards: [
      {
        controls: [
          {
            id: "5950531a-cf35-4851-93f7-d8ad0789dd35",
            isApplicable: true,
            name: "fencing / barriers. signage",
          },
          {
            id: "1c8b8e61-80ed-48da-be40-ea501f3f50de",
            isApplicable: true,
            name: "Traffic control plan",
          },
        ],
        id: "3ff3a096-38dd-4317-a1d1-7a1937895989",
        isApplicable: true,
        name: "Congested work space / crowding",
      },
    ],
    incidents: [],
    id: "d46309a6-c8ca-4b82-87c6-e6d5663202fc",
    name: "Urban density / population",
  },
];

const tasks = [
  {
    endDate: "2022-06-11",
    hazards: [
      {
        controls: [
          {
            id: "1646d885-c977-4dca-9145-53ec54e0817e",
            isApplicable: true,
            name: "Situational jobsite awareness",
          },
        ],
        id: "08b036ba-c19e-4c8d-b75c-dec07ff266e3",
        isApplicable: true,
        name: "Caught in between bevel machine",
      },
      {
        controls: [
          {
            id: "a1547c96-17aa-4b70-80f1-bb6ccf6ce39e",
            isApplicable: true,
            name: "Double eye protection",
          },
        ],
        id: "5b85c7ff-56ff-4f5d-a198-d1c5428b37e6",
        isApplicable: true,
        name: "Flying debris",
      },
    ],
    incidents: [],
    id: "d17b2a0c-d63a-4e62-9d5f-caf7f25ce6f1",
    name: "Above-ground welding - Pipe face beveling",
    riskLevel: RiskLevel.HIGH,
    startDate: "2022-05-05",
    status: TaskStatus.IN_PROGRESS,
  },
];

describe(JobHazardAnalysis.name, () => {
  mockTenantStore();
  describe("when does not have tasks and/or site conditions", () => {
    it.each([null, undefined, {}, []])(
      "should display with the empty state for each section",
      list => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        render(<JobHazardAnalysis tasks={list} siteConditions={list} />);

        screen.getByText(
          /There are currently no site conditions that have been selected between the set contractor start and end dates/i
        );
        screen.getByText(
          /There are currently no activity tasks that have been selected between the set contractor start and end dates/i
        );
      }
    );
  });

  describe("when we are creating a new report", () => {
    beforeEach(() => {
      formRender(
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        <JobHazardAnalysis tasks={tasks} siteConditions={siteConditions} />
      );
    });

    describe("when we have site conditions", () => {
      it("should render the site condition name", () => {
        screen.getByText(/Urban density \/ population/i);
      });
      it("should render the hazard name", () => {
        screen.getByText(/Congested work space \/ crowding/i);
      });
      it("should render the hazards' controls", () => {
        screen.getByText(/fencing \/ barriers. signage/i);
        screen.getByText(/Traffic control plan/i);
      });
    });

    describe("when we have tasks", () => {
      it("should render the task name", () => {
        screen.getByText(/Above-ground welding - Pipe face beveling/i);
      });
      it("should render the hazard name", () => {
        screen.getByText(/Caught in between bevel machine/i);
        screen.getByText(/Flying debris/i);
      });
      it("should render the hazards' controls", () => {
        screen.getByText(/Situational jobsite awareness/i);
        screen.getByText(/Double eye protection/i);
      });
    });
  });

  describe("when report is in progress", () => {
    beforeEach(() => {
      formRender(
        <JobHazardAnalysis
          tasks={tasks}
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          siteConditions={siteConditions}
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          defaultValues={{}}
        />
      );
    });

    describe("when we have site conditions", () => {
      it("should render the site condition name", () => {
        screen.getByText(/Urban density \/ population/i);
      });
      it("should render the hazard name", () => {
        screen.getByText(/Congested work space \/ crowding/i);
      });
      it("should render the hazards' controls", () => {
        screen.getByText(/fencing \/ barriers. signage/i);
        screen.getByText(/Traffic control plan/i);
      });
    });

    describe("when we have tasks", () => {
      it("should render the task name", () => {
        screen.getByText(/Above-ground welding - Pipe face beveling/i);
      });
      it("should render the hazard name", () => {
        screen.getByText(/Caught in between bevel machine/i);
        screen.getByText(/Flying debris/i);
      });
      it("should render the hazards' controls", () => {
        screen.getByText(/Situational jobsite awareness/i);
        screen.getByText(/Double eye protection/i);
      });
    });
  });

  describe("when report is completed", () => {
    const defaultValues = {
      sectionIsValid: false,
      siteConditions: [
        {
          hazards: [
            {
              controls: [
                {
                  id: "5950531a-cf35-4851-93f7-d8ad0789dd35",
                  implemented: true,
                  name: "fencing / barriers. signage",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "1c8b8e61-80ed-48da-be40-ea501f3f50de",
                  implemented: false,
                  name: "Traffic control plan",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
              ],
              id: "3ff3a096-38dd-4317-a1d1-7a1937895989",
              isApplicable: true,
              name: "Congested work space / crowding",
            },
          ],
          id: "d46309a6-c8ca-4b82-87c6-e6d5663202fc",
          isApplicable: true,
          name: "Urban density / population",
        },
      ],
      tasks: [
        {
          hazards: [
            {
              controls: [
                {
                  id: "1646d885-c977-4dca-9145-53ec54e0817e",
                  implemented: true,
                  name: "Situational jobsite awareness",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
              ],
              id: "08b036ba-c19e-4c8d-b75c-dec07ff266e3",
              isApplicable: true,
              name: "Caught in between bevel machine",
              notApplicableReason: null,
            },
            {
              controls: [
                {
                  id: "a1547c96-17aa-4b70-80f1-bb6ccf6ce39e",
                  implemented: false,
                  name: "Double eye protection",
                  notImplementedReason: "Other controls in place",
                  furtherExplanation: "",
                },
                {
                  id: "ba060df4-5a90-4319-b22e-ccb89d30b235",
                  implemented: true,
                  name: "Eye protection",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "28c27bef-b988-4886-b77b-9eb61cbd674d",
                  implemented: true,
                  name: "Face shield",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
              ],
              id: "5b85c7ff-56ff-4f5d-a198-d1c5428b37e6",
              isApplicable: true,
              name: "Flying debris",
              notApplicableReason: null,
            },
            {
              controls: [
                {
                  id: "3ba4647e-1f9a-4fde-94b7-6fbf143b4c12",
                  implemented: null,
                  name: "Impact rated gloves",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
              ],
              id: "7a448108-aeb2-4f00-b43a-ef716fa13167",
              isApplicable: false,
              name: "Sharp edges/metal shavings",
              notApplicableReason: null,
            },
            {
              controls: [
                {
                  id: "8752d6a4-89fb-42ab-9d14-5d57de259786",
                  implemented: null,
                  name: "811 locate tickets in place and utilities clearly marked",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "64ba2459-078c-4018-a4a7-43d743007445",
                  implemented: null,
                  name: "Fill in gaps and holes in mats",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "08ea8901-0edc-4f66-9ea3-3386584f9efe",
                  implemented: null,
                  name: "Housekeeping",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "b2647e4e-0afb-4028-8609-b2597663abf4",
                  implemented: null,
                  name: "Proper ladder usage",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
                {
                  id: "6179a756-e3a4-48c7-b2d9-1fec8c82fe83",
                  implemented: null,
                  name: "Situational jobsite awareness",
                  notImplementedReason: "",
                  furtherExplanation: "",
                },
              ],
              id: "2142f66e-23cc-4934-899a-e3cee18ebcf1",
              isApplicable: false,
              name: "Slips, trips, falls",
              notApplicableReason: null,
            },
          ],
          id: "d17b2a0c-d63a-4e62-9d5f-caf7f25ce6f1",
          name: "Above-ground welding - Pipe face beveling",
          notApplicableReason: "",
          notes: "",
          performed: true,
          sectionIsValid: null,
        },
      ],
    };

    describe("when tasks and/or site conditions are removed", () => {
      it("should still render the task and site condition name according to the stored report data", () => {
        formRender(
          <JobHazardAnalysis
            tasks={[]}
            siteConditions={[]}
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            defaultValues={defaultValues}
            isCompleted
          />
        );
        screen.getByText(/Urban density \/ population/i);
        screen.getByText(/Above-ground welding - Pipe face beveling/i);
      });

      it("should still render the hazards name according to the stored report data", () => {
        formRender(
          <JobHazardAnalysis
            tasks={[]}
            siteConditions={[]}
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            defaultValues={defaultValues}
            isCompleted
          />
        );
        screen.getByText(/Congested work space \/ crowding/i);
        screen.getByText(/Caught in between bevel machine/i);
        screen.getByText(/Flying debris/i);
      });

      it("should still render the controls name according to the stored report data", () => {
        formRender(
          <JobHazardAnalysis
            tasks={[]}
            siteConditions={[]}
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            defaultValues={defaultValues}
            isCompleted
          />
        );
        screen.getByText(/fencing \/ barriers. signage/i);
        screen.getByText(/Traffic control plan/i);
        screen.getByText(/Situational jobsite awareness/i);
        screen.getByText(/Double eye protection/i);
      });
    });
  });
});
