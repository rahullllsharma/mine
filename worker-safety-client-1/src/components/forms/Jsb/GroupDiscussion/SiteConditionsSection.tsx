import type {
  HazardControl,
  HazardControlId,
  HazardId,
  Jsb,
  LibrarySiteCondition,
  LibrarySiteConditionId,
  LibraryTask,
} from "@/api/codecs";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type { Either } from "fp-ts/lib/Either";
import { useMemo } from "react";
import { flow, pipe } from "fp-ts/lib/function";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import * as M from "fp-ts/lib/Map";
import * as SG from "fp-ts/lib/Semigroup";
import { sequenceS } from "fp-ts/lib/Apply";
import { deferredToOption } from "@/utils/deferred";
import {
  eqHazardControlId,
  eqHazardId,
  eqLibrarySiteConditionId,
  ordHazardControlId,
} from "@/api/codecs";
import { Card } from "../../Basic/Card";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type SiteConditionsSectionData = {
  siteConditionIds: Set<LibrarySiteConditionId>;
  controlIds: Map<HazardId, Set<HazardControlId>>;
};

export const init = (jsb: Jsb): Either<string, SiteConditionsSectionData> =>
  sequenceS(E.Apply)({
    siteConditionIds: pipe(
      jsb.siteConditionSelections,
      E.fromOption(() => "siteConditionSelections is missing"),
      E.map(
        flow(
          A.filter(({ selected }) => selected),
          A.map(({ id }) => id),
          S.fromArray(eqLibrarySiteConditionId)
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

export type SiteConditionsSectionProps = SiteConditionsSectionData & {
  tasksLibrary: Deferred<ApiResult<LibraryTask[]>>;
  siteConditionsLibrary: Deferred<ApiResult<LibrarySiteCondition[]>>;
  onClickEdit?: () => void;
};

export function View(props: SiteConditionsSectionProps): JSX.Element {
  const allControls = useMemo(
    () =>
      pipe(
        props.siteConditionsLibrary,
        deferredToOption,
        O.chain(O.fromEither),
        O.getOrElse((): LibrarySiteCondition[] => []),
        A.chain(task => task.hazards),
        A.chain(hazard => hazard.controls),
        A.map((control): [HazardControlId, HazardControl] => [
          control.id,
          control,
        ]),
        M.fromFoldable(eqHazardControlId, SG.last<HazardControl>(), A.Foldable)
      ),
    [props.siteConditionsLibrary]
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

  const siteConditions = useMemo(
    () =>
      pipe(
        props.siteConditionsLibrary,
        deferredToOption,
        O.chain(O.fromEither),
        O.getOrElse((): LibrarySiteCondition[] => []),
        A.filter(siteCondition =>
          S.elem(eqLibrarySiteConditionId)(siteCondition.id)(
            props.siteConditionIds
          )
        ),
        A.map(siteCondition => ({
          id: siteCondition.id,
          name: siteCondition.name,
          hazards: pipe(
            siteCondition.hazards,
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
      props.siteConditionsLibrary,
      props.siteConditionIds,
      props.controlIds,
      selectedControls,
    ]
  );
  return (
    <GroupDiscussionSection
      title="Site Conditions"
      onClickEdit={props.onClickEdit}
    >
      <div className="flex flex-col gap-4">
        {siteConditions.map(siteCondition => (
          <Card
            key={siteCondition.id}
            name={siteCondition.name}
            hazards={siteCondition.hazards}
          />
        ))}
      </div>
    </GroupDiscussionSection>
  );
}
