import type { HazardAggregator } from "@/types/project/HazardAggregator";
import type {
  SiteConditionAnalysisInputs,
  TaskAnalysisInputs,
} from "@/types/report/DailyReportInputs";
import { screen, fireEvent } from "@testing-library/react";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "../../riskBadge/RiskLevel";
import JobReportCard from "./JobReportCard";

const job: HazardAggregator = {
  id: "1",
  name: "Pipe Face Alignment",
  riskLevel: RiskLevel.MEDIUM,
  startDate: "2021-10-10",
  endDate: "2021-10-11",
  status: TaskStatus.NOT_STARTED,
  isManuallyAdded: false,
  hazards: [
    {
      id: "1",
      name: "Pinch Point",
      isApplicable: true,
      controls: [
        { id: "1", name: "Gloves", isApplicable: true },
        { id: "2", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
    {
      id: "2",
      name: "Struck by Equipment and Material",
      isApplicable: true,
      controls: [
        { id: "3", name: "Gloves", isApplicable: true },
        { id: "4", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
  ],
  incidents: [],
};

describe(JobReportCard.name, () => {
  mockTenantStore();
  describe("when is a Task", () => {
    describe("when a job is toggled on", () => {
      it("should render all available hazards", () => {
        formRender(
          <JobReportCard formGroupKey="tasks" job={job} switchLabel="" />
        );
        const switchElement = screen.getAllByRole("switch");
        /*
        The default state of the switch button is toggled on.
        We fire the click event twice to test if toggling off and back on shows the same results
      */
        fireEvent.click(switchElement[0]);
        fireEvent.click(switchElement[0]);
        const hazardElements = screen.queryAllByTestId("hazard-report-card-", {
          exact: false,
        });
        expect(hazardElements).toHaveLength(job.hazards.length);
      });
    });

    describe("when a job is toggled off", () => {
      it("should hide all hazards", () => {
        formRender(
          <JobReportCard formGroupKey="tasks" job={job} switchLabel="" />
        );

        const switchElement = screen.getAllByRole("switch");
        fireEvent.click(switchElement[0]);
        const hazardElements = screen.queryAllByTestId("hazard-report-card-", {
          exact: false,
        });
        expect(hazardElements).toHaveLength(0);
      });

      it("should display the Select with reasons", async () => {
        formRender(
          <JobReportCard formGroupKey="tasks" job={job} switchLabel="urbint" />
        );

        const switchElement = screen.getAllByRole("switch");
        fireEvent.click(switchElement[0]);
        expect(
          await screen.getByText(/why was this task not performed/gi)
        ).toBeInTheDocument();
      });
    });

    describe("when has a selected job", () => {
      it("should render the toggle on when the task is performed", () => {
        const selectedJob = {
          id: job.id,
          performed: true,
          hazards: [],
        } as unknown as TaskAnalysisInputs;

        formRender(
          <JobReportCard
            formGroupKey="tasks"
            job={job}
            selectedJob={selectedJob}
            switchLabel="urbint"
          />
        );

        expect(
          screen.getByRole("switch", {
            name: /urbint/i,
          })
        ).toBeChecked();
      });

      it("should render the toggle off when the task is not performed", () => {
        const selectedJob = {
          id: job.id,
          performed: false,
          hazards: [],
        } as unknown as TaskAnalysisInputs;

        formRender(
          <JobReportCard
            formGroupKey="tasks"
            job={job}
            selectedJob={selectedJob}
            switchLabel="urbint"
          />
        );

        expect(
          screen.getByRole("switch", {
            name: /urbint/i,
          })
        ).not.toBeChecked();
      });

      it("should have selected reason when the task is not performed and has reasons", () => {
        const selectedJob = {
          id: job.id,
          performed: false,
          hazards: [],
          notApplicableReason: "Equipment Delay",
        } as unknown as TaskAnalysisInputs;

        formRender(
          <JobReportCard
            formGroupKey="tasks"
            job={job}
            selectedJob={selectedJob}
            switchLabel="urbint"
          />
        );

        screen.getByText("Equipment Delay");
      });
    });

    describe("when is a SiteCondition", () => {
      describe("when a job is toggled on", () => {
        it("should render all available hazards", () => {
          formRender(
            <JobReportCard
              formGroupKey="siteConditions"
              job={job}
              switchLabel=""
            />
          );
          const switchElement = screen.getAllByRole("switch");
          /*
        The default state of the switch button is toggled on.
        We fire the click event twice to test if toggling off and back on shows the same results
      */
          fireEvent.click(switchElement[0]);
          fireEvent.click(switchElement[0]);
          const hazardElements = screen.queryAllByTestId(
            "hazard-report-card-",
            {
              exact: false,
            }
          );
          expect(hazardElements).toHaveLength(job.hazards.length);
        });
      });

      describe("when a job is toggled off", () => {
        it("should hide all hazards", () => {
          formRender(
            <JobReportCard
              formGroupKey="siteConditions"
              job={job}
              switchLabel=""
            />
          );

          const switchElement = screen.getAllByRole("switch");
          fireEvent.click(switchElement[0]);
          const hazardElements = screen.queryAllByTestId(
            "hazard-report-card-",
            {
              exact: false,
            }
          );
          expect(hazardElements).toHaveLength(0);
        });

        it("should NOT display the Select", async () => {
          formRender(
            <JobReportCard
              formGroupKey="siteConditions"
              job={job}
              switchLabel="urbint"
            />
          );

          const switchElement = screen.getAllByRole("switch");
          fireEvent.click(switchElement[0]);
          expect(
            await screen.queryByText(/why was this task not performed/gi)
          ).not.toBeInTheDocument();
        });
      });

      describe("when has a selected job", () => {
        it("should render the toggle on when the site condition is applicable", () => {
          const selectedJob = {
            id: job.id,
            isApplicable: true,
            hazards: [],
          } as unknown as SiteConditionAnalysisInputs;

          formRender(
            <JobReportCard
              formGroupKey="siteConditions"
              job={job}
              selectedJob={selectedJob}
              switchLabel="urbint"
            />
          );

          expect(
            screen.getByRole("switch", {
              name: /urbint/i,
            })
          ).toBeChecked();
        });

        it("should render the toggle off when the task is not performed", () => {
          const selectedJob = {
            id: job.id,
            isApplicable: false,
            hazards: [],
          } as unknown as SiteConditionAnalysisInputs;

          formRender(
            <JobReportCard
              formGroupKey="siteConditions"
              job={job}
              selectedJob={selectedJob}
              switchLabel="urbint"
            />
          );

          expect(
            screen.getByRole("switch", {
              name: /urbint/i,
            })
          ).not.toBeChecked();
        });
      });
    });
  });
});
