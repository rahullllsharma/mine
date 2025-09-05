import type { Either } from "fp-ts/lib/Either";
import type { SummaryDataGenerationError } from ".";
import type { SummarySectionWrapperOnClickEdit } from "./summarySectionWrapper";
import type {
  Incident,
  IncidentId,
  LibraryTask,
  LibraryTaskId,
} from "@/api/codecs";
import type { TaskHistoricalIncidents } from "../Wizard";
import type { Option } from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as SG from "fp-ts/lib/Semigroup";
import * as Tup from "fp-ts/lib/Tuple";
import * as Eq from "fp-ts/lib/Eq";
import * as A from "fp-ts/lib/Array";
import { Eq as EqString } from "fp-ts/lib/string";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import { constVoid, pipe } from "fp-ts/lib/function";
import EboIncidentCard from "@/components/incidentCard/EboIncidentCard";
import { eqLibraryTaskId, ordLibraryTaskId } from "@/api/codecs";
import { TaskCard } from "../../Basic/TaskCard";
import SummarySectionWrapper from "./summarySectionWrapper";

export type HistoricIncidentsData = {
  selectedIncidentIds: Set<IncidentId>;
  tasks: LibraryTask[];
  selectedTaskIncidents: TaskHistoricalIncidents[];
};

export type HistoricIncidentsSummarySectionProps =
  SummarySectionWrapperOnClickEdit & {
    data: Either<SummaryDataGenerationError, HistoricIncidentsData>;
    isReadOnly?: boolean;
  };

export const eqHistoricalIncidentId = Eq.contramap((id: IncidentId) => id)(
  EqString
);

function HistoricIncidentsSummarySection({
  onClickEdit,
  data,
  isReadOnly = false,
}: HistoricIncidentsSummarySectionProps) {
  const generateTaskListForSelectedIncidents =
    (selectedTaskIncidents: TaskHistoricalIncidents[]) =>
    (tasks: LibraryTask[]) =>
    (
      selectedIncidentIds: Set<IncidentId>
    ): { selectedIncidents: Incident[]; task: Option<LibraryTask> }[] =>
      pipe(
        selectedTaskIncidents,
        A.filter(t => A.isNonEmpty(t.result)),
        A.map((t): [LibraryTaskId, Incident[]] => [t.taskId, t.result]),
        M.fromFoldable(eqLibraryTaskId, SG.last<Incident[]>(), A.Foldable),
        M.filter(result =>
          pipe(
            result,
            A.some(a =>
              S.elem(eqHistoricalIncidentId)(a.id)(selectedIncidentIds)
            )
          )
        ),
        M.mapWithIndex((taskId, result) => ({
          task: pipe(
            tasks,
            A.findFirst(task => task.id === taskId)
          ),
          selectedIncidents: pipe(
            result,
            A.filter(incident =>
              S.elem(eqHistoricalIncidentId)(incident.id)(selectedIncidentIds)
            )
          ),
        })),
        M.toArray(ordLibraryTaskId),
        A.map(Tup.snd)
      );

  return (
    <SummarySectionWrapper
      title="Historical Incidents"
      onClickEdit={onClickEdit}
      isEmpty={E.isLeft(data)}
      isEmptyText="No historical incidents is selected."
      isReadOnly={isReadOnly}
    >
      {E.isRight(data) && (
        <div className="flex flex-col gap-5">
          {pipe(
            generateTaskListForSelectedIncidents(
              data.right.selectedTaskIncidents
            )(data.right.tasks)(data.right.selectedIncidentIds),
            A.map(
              taskWithSelectedIncidents =>
                O.isSome(taskWithSelectedIncidents.task) && (
                  <div key={taskWithSelectedIncidents.task.value.id}>
                    <TaskCard
                      title={taskWithSelectedIncidents.task.value.name}
                      risk={taskWithSelectedIncidents.task.value.riskLevel}
                      showRiskInformation={false}
                      showRiskText={false}
                      withLeftBorder={false}
                      isReadOnly={isReadOnly}
                      isExpanded={true}
                    >
                      {pipe(
                        taskWithSelectedIncidents.selectedIncidents,
                        O.fromPredicate(A.isNonEmpty),
                        O.fold(
                          () => (
                            <div className="w-full flex justify-center items-center p-4">
                              No historical hazards were selected.
                            </div>
                          ),
                          selectedIncidents => (
                            <>
                              {pipe(
                                selectedIncidents,
                                A.map(incident => (
                                  <EboIncidentCard
                                    key={incident.id}
                                    incident={incident}
                                    onSelect={constVoid}
                                    selected={true}
                                  />
                                ))
                              )}
                            </>
                          )
                        )
                      )}
                    </TaskCard>
                  </div>
                )
            )
          )}
        </div>
      )}
    </SummarySectionWrapper>
  );
}

export default HistoricIncidentsSummarySection;
