import type {
  LibraryRegion,
  LibraryDivision,
  Contractor,
} from "@/api/generated/types";
import type { FilterProject } from "@/container/insights/utils";
import React from "react";
import LearningsPage from "@/container/learnings/learnings";
import PlanningPage from "@/container/planning/planning";

type PlanningAndLearning = {
  projects?: FilterProject[];
  regions?: LibraryRegion[];
  divisions?: LibraryDivision[];
  contractors?: Contractor[];
  isPlanningEnable: boolean;
  isLearningEnable: boolean;
};
type PlanningPageProps = {
  activeInsightId: string;
  planningAndLearning: PlanningAndLearning;
  displayProjectTaskRiskHeatmap?: boolean;
};
function PlanningAndLearningReportType({
  activeInsightId,
  planningAndLearning,
  displayProjectTaskRiskHeatmap,
}: PlanningPageProps) {
  return (
    <>
      {activeInsightId === "plannings" && (
        <PlanningPage
          projects={planningAndLearning.projects ?? []}
          regions={planningAndLearning.regions ?? []}
          contractors={planningAndLearning.contractors ?? []}
          divisions={planningAndLearning.divisions ?? []}
          displayProjectTaskRiskHeatmap={displayProjectTaskRiskHeatmap}
        />
      )}
      {activeInsightId === "learnings" && (
        <LearningsPage
          projects={planningAndLearning.projects ?? []}
          regions={planningAndLearning.regions ?? []}
          contractors={planningAndLearning.contractors ?? []}
          divisions={planningAndLearning.divisions ?? []}
        />
      )}
    </>
  );
}

export default PlanningAndLearningReportType;
