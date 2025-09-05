import type { PropsWithChildren } from "react";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { DailyReport } from "@/types/report/DailyReport";
import type { Project } from "@/types/project/Project";
import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import { getFormattedLocaleDateTime } from "@/utils/date/helper";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import WorkSchedule from "../workSchedule/WorkSchedule";
import SafetyAndCompliance from "../safetyAndCompliance/SafetyAndCompliance";
import JobHazardAnalysis from "../jobHazardAnalysis/JobHazardAnalysis";
import CrewInformation from "../crew/information/CrewInformation";
import AdditionalInformation from "../additionalInformation/AdditionalInformation";
import ProjectPrintInfo from "./projectPrintInfo/ProjectPrintInfo";

type PrintReportProps = {
  project: Project;
  report: DailyReport;
};

type PrintSectionProps = PropsWithChildren<{
  title: string;
}>;

const PrintSection = ({
  title,
  className,
  children,
}: PropsWithClassName<PrintSectionProps>): JSX.Element => (
  <section className={cx("print-section", className)}>
    <h2 className="text-2xl font-semibold text-neutral-shade-100 mb-4">
      {title}
    </h2>
    {children}
  </section>
);

export default function PrintReport({
  project,
  report,
}: PrintReportProps): JSX.Element {
  const { workPackage, control } = useTenantStore(state =>
    state.getAllEntities()
  );
  const { sections } = report as { sections: DailyReportInputs };

  const { workSchedule, jobHazardAnalysis, crew } = sections;
  const startDateTime = getFormattedLocaleDateTime(
    workSchedule?.startDatetime || ""
  );
  const endDateTime = getFormattedLocaleDateTime(
    workSchedule?.endDatetime || ""
  );

  // Creating an entry based on the selected option to show on the print page
  const contractors = crew?.contractor
    ? [{ id: crew?.contractor, name: crew?.contractor }]
    : undefined;

  return (
    <main className="print-page">
      <PrintSection title={`${workPackage.label} Information`}>
        <ProjectPrintInfo report={report} project={project} />
      </PrintSection>
      <PrintSection title="Work Schedule">
        <WorkSchedule
          startDatetime={startDateTime}
          endDatetime={endDateTime}
          isCompleted
          dateLimits={{ projectStartDate: "", projectEndDate: "" }}
        />
      </PrintSection>
      <PrintSection
        title={`${control.labelPlural} Assessment`}
        className="control-assessment"
      >
        <JobHazardAnalysis
          siteConditions={[]}
          tasks={[]}
          defaultValues={jobHazardAnalysis}
          isCompleted
        />
      </PrintSection>
      <PrintSection title="Safety & Compliance">
        <SafetyAndCompliance isCompleted />
      </PrintSection>
      <PrintSection title="Crew">
        <CrewInformation companies={contractors} isCompleted />
      </PrintSection>
      <PrintSection title="Additional Information">
        <AdditionalInformation isCompleted />
      </PrintSection>
    </main>
  );
}
