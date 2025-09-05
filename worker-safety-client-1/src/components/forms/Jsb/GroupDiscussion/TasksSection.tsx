import type {
  HazardControl,
  HazardControlId,
  HazardId,
  Jsb,
  LibraryTask,
  LibraryTaskId,
} from "@/api/codecs";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type { Either } from "fp-ts/lib/Either";
import * as S from "fp-ts/lib/Set";
import * as A from "fp-ts/lib/Array";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import * as SG from "fp-ts/lib/Semigroup";
import { flow, pipe } from "fp-ts/lib/function";
import { useMemo } from "react";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import { RiskLevel } from "@/api/generated/types";
import {
  eqHazardControlId,
  eqHazardId,
  eqLibraryTaskId,
  ordHazardControlId,
} from "@/api/codecs";
import { deferredToOption } from "@/utils/deferred";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";
import { Card } from "../../Basic/Card";

export type TasksSectionData = {
  taskIds: Set<LibraryTaskId>;
  controlIds: Map<HazardId, Set<HazardControlId>>;
};

export const init = (jsb: Jsb): Either<string, TasksSectionData> =>
  sequenceS(E.Apply)({
    taskIds: pipe(
      jsb.taskSelections,
      E.fromOption(() => "taskSelections is missing"),
      E.map(
        flow(
          A.map(({ id }) => id),
          S.fromArray(eqLibraryTaskId)
        )
      )
    ),
    controlIds: pipe(
      jsb.controlAssessmentSelections,
      E.fromOption(() => "controlAssessmentSelections is missing"),
      E.map(
        flow(
          A.map((ctrl): [HazardId, Set<HazardControlId>] => [
            ctrl.hazardId,
            pipe(ctrl.controlIds, S.fromArray(eqHazardControlId)),
          ]),
          M.fromFoldable(
            eqHazardId,
            S.getUnionSemigroup(eqHazardControlId),
            A.Foldable
          )
        )
      )
    ),
  });

export type TasksSectionProps = TasksSectionData & {
  tasksLibrary: Deferred<ApiResult<LibraryTask[]>>;
  riskLevels: Map<LibraryTaskId, RiskLevel>;
  onClickEdit?: () => void;
};

export function View(props: TasksSectionProps): JSX.Element {
  const tasksLibrary = useMemo(
    () =>
      pipe(
        props.tasksLibrary,
        deferredToOption,
        O.chain(O.fromEither),
        O.getOrElse((): LibraryTask[] => [])
      ),
    [props.tasksLibrary]
  );

  const allControls: Map<HazardControlId, HazardControl> = useMemo(
    () =>
      pipe(
        tasksLibrary,
        A.chain(task => task.hazards),
        A.chain(hazard => hazard.controls),
        A.map((control): [HazardControlId, HazardControl] => [
          control.id,
          control,
        ]),
        M.fromFoldable(eqHazardControlId, SG.last<HazardControl>(), A.Foldable)
      ),
    [tasksLibrary]
  );

  const selectedControls: Map<HazardId, HazardControl[]> = useMemo(
    () =>
      pipe(
        props.controlIds,
        M.map(controlIds =>
          pipe(
            controlIds,
            S.toArray(ordHazardControlId),
            A.filterMap(controlId =>
              M.lookup(eqHazardControlId)(controlId)(allControls)
            )
          )
        )
      ),
    [props.controlIds, allControls]
  );

  const tasks = useMemo(
    () =>
      pipe(
        tasksLibrary,
        A.filter(task => S.elem(eqLibraryTaskId)(task.id)(props.taskIds)),
        A.map(task => ({
          id: task.id,
          name: task.name,
          riskLevel: pipe(
            M.lookup(eqLibraryTaskId)(task.id)(props.riskLevels),
            O.getOrElseW(() =>
              pipe(
                tasksLibrary,
                A.findFirst(t => t.id === task.id),
                O.fold(
                  () => RiskLevel.Unknown,
                  tsk => tsk.riskLevel
                )
              )
            )
          ),
          hazards: pipe(
            task.hazards,
            A.filter(hazard =>
              M.member(eqHazardId)(hazard.id)(props.controlIds)
            ),
            A.map(hazard => ({
              ...hazard,
              // controls list on the hazard is containing only the default controls
              // replacing the controls on the hazard with the selected controls
              controls: pipe(
                M.lookup(eqHazardId)(hazard.id)(selectedControls),
                O.getOrElseW(() => [])
              ),
            }))
          ),
        }))
      ),
    [
      tasksLibrary,
      props.taskIds,
      selectedControls,
      props.riskLevels,
      props.controlIds,
    ]
  );

  return (
    <GroupDiscussionSection title="Tasks" onClickEdit={props.onClickEdit}>
      <div className="flex flex-col gap-4">
        {tasks.map(task => (
          <Card
            key={`${task.id}`}
            name={task.name}
            riskLevel={task.riskLevel}
            hazards={task.hazards}
          />
        ))}
      </div>
    </GroupDiscussionSection>
  );
}
