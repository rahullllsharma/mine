import type { FormField } from "@/utils/formField";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type {
  ActivitiesGroupId,
  Hazard,
  HazardId,
  HazardObservation,
  LibraryTask,
  LibraryTaskId,
  HazardControlConnectorId,
  TaskHazardConnectorId,
} from "@/api/codecs";
import type { EboHighEnergyTaskConceptInput } from "@/api/generated/types";
import type { eboFormValidationError } from "../Wizard";
import type { Option } from "fp-ts/lib/Option";
import type { StepSnapshot } from "../../Utils";
import type * as t from "io-ts";
import { NumberFromString } from "io-ts-types";
import { v4 as uuid } from "uuid";
import * as tt from "io-ts-types";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as EQ from "fp-ts/Eq";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import * as string from "fp-ts/lib/string";
import * as Tup from "fp-ts/lib/Tuple";
import { Eq as eqNumber, Ord as ordNumber } from "fp-ts/number";
import { Eq as eqString, Ord as ordString } from "fp-ts/string";
import { match as matchBoolean } from "fp-ts/boolean";
import { flow, pipe } from "fp-ts/lib/function";
import { SectionHeading } from "@urbint/silica";
import { useMemo } from "react";
import { initFormField, updateFormField } from "@/utils/formField";
import { optionFromString } from "@/utils/validation";
import { ControlType, ApplicabilityLevel, eqHazardId } from "@/api/codecs";
import { noEffect } from "@/utils/reducerWithEffect";
import StepLayout from "@/components/forms/StepLayout";
import { messages } from "@/locales/messages";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import {
  getUncontrolledReasons,
  getTenantName,
} from "../TenantLabel/LabelOnBasisOfTenant";
import { TaskCard } from "../../Basic/TaskCard";
import { Dialog } from "../../Basic/Dialog";
import HazardWrapper from "../Hazards/HazardWrapper";
import { scrollTopEffect, snapshotHashMap, snapshotMap } from "../../Utils";

export type HazardFieldValues = {
  hazardControlConnectorId: Option<HazardControlConnectorId>;
  description: string;
  energyLevel: FormField<t.Errors, string, Option<number>>;
  isDirectControlsImplemented: Option<boolean>;
  directControls: Set<string>;
  noDirectControls: Option<string>;
  limitedControls: Set<string>;
  directControlDescription: string;
  limitedControlDescription: string;
};

export type DuplicateSelectedHazards = Map<number, HazardFieldValues>;
export type SelectedHazards = Map<HazardId, DuplicateSelectedHazards>;

export type HighEnergyTaskSubSectionErrors = "NO_HAZARD_SELECTED";

export const OTHER_CONTROL_NAME = "Other";
export const OTHER_HAZARD_NAME = "Other";

export const highEnergyTaskSubSectionErrorTexts = (
  error: HighEnergyTaskSubSectionErrors
) => {
  switch (error) {
    case "NO_HAZARD_SELECTED": {
      return "At least one high energy hazard must be identified as observed/present.";
    }
  }
};

export const energyLevelValidation = (el: string): boolean =>
  pipe(
    el,
    string.isEmpty,
    matchBoolean(
      () =>
        pipe(
          el,
          NumberFromString.decode,
          E.map(e => e >= 500),
          E.getOrElse(() => false)
        ),
      () => false
    )
  );

export const getHazardControlNameOfControlId =
  (hazards: Hazard[]) => (controlId: string) => {
    return pipe(
      hazards,
      A.map(h => h.controls),
      A.flatten,
      A.findFirst(control => control.id === controlId),
      O.map(control => control.name),
      O.getOrElse(() => "")
    );
  };

export const getHazardNameOfHazardId =
  (hazards: Hazard[]) => (hazardId: HazardId) => {
    return pipe(
      hazards,
      A.findFirst(hazard => hazard.id === hazardId),
      O.map(hazard => hazard.name),
      O.getOrElse(() => "")
    );
  };

export const initialSelectedHazardData: HazardFieldValues = {
  hazardControlConnectorId: O.none,
  description: "",
  energyLevel: initFormField<t.Errors, string, Option<number>>(
    optionFromString(tt.NumberFromString).decode
  )(""),
  isDirectControlsImplemented: O.none,
  directControls: new Set<string>(),
  noDirectControls: O.none,
  limitedControls: new Set<string>(),
  directControlDescription: "",
  limitedControlDescription: "",
};

export type Model = {
  activityName: string;
  activityId: ActivitiesGroupId;
  taskId: LibraryTaskId;
  instanceId: number;
  taskHazardConnectorId: TaskHazardConnectorId;
  selectedHazards: SelectedHazards;
  recommendedHazardDialog: Option<boolean>;
  error: Option<HighEnergyTaskSubSectionErrors>;
  savedHazardNames: Map<HazardId, string>;
  savedControlNames: Map<string, string>;
};

const populateHazardFieldValues = (
  obv: HazardObservation
): HazardFieldValues => ({
  hazardControlConnectorId: obv.hazardControlConnectorId,
  description: O.isSome(obv.description) ? obv.description.value : "",
  energyLevel: initFormField<t.Errors, string, Option<number>>(
    optionFromString(tt.NumberFromString).decode
  )(O.isSome(obv.energyLevel) ? obv.energyLevel.value : ""),
  isDirectControlsImplemented: obv.directControlsImplemented,
  directControls: pipe(
    obv.directControls,
    O.map(A.map(dc => dc.id)),
    O.map(S.fromArray(eqString)),
    O.getOrElse(() => new Set())
  ),
  noDirectControls: obv.reason,
  limitedControls: pipe(
    obv.limitedControls,
    O.map(A.map(lc => lc.id)),
    O.map(S.fromArray(eqString)),
    O.getOrElse(() => new Set())
  ),
  directControlDescription: O.isSome(obv.directControlDescription)
    ? obv.directControlDescription.value
    : "",
  limitedControlDescription: O.isSome(obv.limitedControlDescription)
    ? obv.limitedControlDescription.value
    : "",
});

const initiateHazardFieldValues = (
  obv: HazardObservation,
  index: number
): Map<number, HazardFieldValues> =>
  pipe(
    new Map<number, HazardFieldValues>(),
    M.upsertAt(eqNumber)(index, populateHazardFieldValues(obv))
  );

const shouldAddNewHazard = (
  hazards: DuplicateSelectedHazards
): O.Option<number> =>
  pipe(
    hazards,
    M.size,
    O.fromPredicate(size => size < 6)
  );

const generateNewDuplicateHazardIdx = (
  hazards: DuplicateSelectedHazards
): O.Option<number> =>
  pipe(
    hazards,
    M.keys(ordNumber),
    A.last,
    O.map(lastIdx => lastIdx + 1)
  );

export const generateSelectedHazardObservations = (
  observations: HazardObservation[]
): SelectedHazards =>
  pipe(
    observations,
    A.reduce(new Map<HazardId, DuplicateSelectedHazards>(), (output, obv) => {
      if (!obv.observed) return output;

      return pipe(
        output,
        M.lookup(eqHazardId)(obv.id),
        O.fold(
          () =>
            pipe(
              output,
              M.upsertAt(eqHazardId)(obv.id, initiateHazardFieldValues(obv, 0))
            ),
          () => {
            return pipe(
              output,
              M.modifyAt(eqHazardId)(obv.id, hazards =>
                pipe(
                  hazards,
                  generateNewDuplicateHazardIdx,
                  O.map(idx =>
                    pipe(
                      hazards,
                      M.upsertAt(eqNumber)(idx, populateHazardFieldValues(obv))
                    )
                  ),
                  O.getOrElse(() => hazards)
                )
              ),
              O.getOrElse(() => output)
            );
          }
        )
      );
    })
  );

export const extractSavedHazardNames = (
  observations: HazardObservation[]
): Map<HazardId, string> =>
  pipe(
    observations,
    A.reduce(new Map<HazardId, string>(), (output, obv) => {
      output.set(obv.id, obv.name);
      return output;
    })
  );

export const extractSavedControlNames = (
  observations: HazardObservation[]
): Map<string, string> => {
  const controlNames = new Map<string, string>();

  observations.forEach(obv => {
    pipe(
      obv.directControls,
      O.map(controls =>
        controls.forEach(control => {
          controlNames.set(control.id, control.name);
        })
      )
    );
    pipe(
      obv.limitedControls,
      O.map(controls =>
        controls.forEach(control => {
          controlNames.set(control.id, control.name);
        })
      )
    );
  });

  return controlNames;
};

const checkHazardApplicabilityLevel =
  (taskId: LibraryTaskId) => (hazard: Hazard) =>
    pipe(
      hazard.taskApplicabilityLevels,
      A.filter(tal => EQ.eqStrict.equals(tal.taskId, taskId)),
      A.filter(tal =>
        EQ.eqStrict.equals(tal.applicabilityLevel, ApplicabilityLevel.MOSTLY)
      ),
      A.isNonEmpty
    );

export const getRecommendedHazards = (
  hazards: Hazard[],
  selectedHazards: SelectedHazards,
  taskId: LibraryTaskId
) => {
  return pipe(
    hazards,
    A.filter(checkHazardApplicabilityLevel(taskId)),
    A.filter(hazard => !selectedHazards.has(hazard.id))
  );
};

export const getOtherControlName = (controlType: ControlType) => {
  switch (controlType) {
    case ControlType.DIRECT:
      return OTHER_CONTROL_NAME;
    case ControlType.INDIRECT:
      return OTHER_CONTROL_NAME;
  }
};

export const getOtherControlId =
  (hazards: Hazard[]) => (hazardId: string) => (controlType: ControlType) =>
    pipe(
      hazards,
      A.findFirst(h => h.id === hazardId),
      O.chain(h =>
        pipe(
          h.controls,
          A.filter(
            control =>
              O.isSome(control.controlType) &&
              control.controlType.value === controlType
          ),
          A.filter(
            control => control.name === getOtherControlName(controlType)
          ),
          A.map(control => control.id),
          A.head
        )
      )
    );

export const getOtherHazardId = (hazards: Hazard[]) =>
  pipe(
    hazards,
    A.findFirst(h => h.name === OTHER_HAZARD_NAME),
    O.map(h => h.id)
  );

export function init(
  activityName: string,
  activityId: ActivitiesGroupId,
  taskId: LibraryTaskId,
  instanceId: number,
  taskHazardConnectorId: TaskHazardConnectorId,
  hazards: O.Option<SelectedHazards>,
  savedHazardNames: Map<HazardId, string> = new Map(),
  savedControlNames: Map<string, string> = new Map()
): Model {
  return {
    activityName: activityName,
    activityId: activityId,
    taskId: taskId,
    instanceId: instanceId,
    taskHazardConnectorId,
    selectedHazards: O.isSome(hazards) ? hazards.value : new Map(),
    recommendedHazardDialog: O.none,
    error: O.none,
    savedHazardNames,
    savedControlNames,
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return pipe({
    activityName: model.activityName,
    activityId: model.activityId,
    taskId: model.taskId,
    instanceId: model.instanceId,
    taskHazardConnectorId: model.taskHazardConnectorId,
    selectedHazards: pipe(
      model.selectedHazards,
      M.map(snapshotHashMap(ordNumber)),
      snapshotMap
    ),
  });
};

export type Action =
  | {
      type: "HazardObserved";
      value: boolean;
      id: HazardId;
    }
  | {
      type: "CopyObservedHazard";
      id: HazardId;
    }
  | {
      type: "DeleteObservedHazardCopy";
      hazardId: HazardId;
      copyId: number;
    }
  | {
      type: "ChangeHazardDescription";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "ChangeEnergyLevel";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "ToggleIsDirectControlsImplemented";
      hazardId: HazardId;
      copyId: number;
      value: O.Option<boolean>;
    }
  | {
      type: "SelectedDirectControl";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "RemovedDirectControl";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "ChangeDirectControlsDescription";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "SelectedNoDirectControlReason";
      hazardId: HazardId;
      copyId: number;
      value: O.Option<string>;
    }
  | {
      type: "SelectedLimitedControl";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "RemovedLimitedControl";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | {
      type: "ChangeLimitedControlsDescription";
      hazardId: HazardId;
      copyId: number;
      value: string;
    }
  | { type: "ShowRecommendedHazardDialog" }
  | { type: "CloseRecommendedHazardDialog" }
  | { type: "ShowError"; errorType: HighEnergyTaskSubSectionErrors };

export const HazardObserved =
  (id: HazardId) =>
  (value: boolean): Action => ({
    type: "HazardObserved",
    value,
    id,
  });

export const CopyObservedHazard = (id: HazardId): Action => ({
  type: "CopyObservedHazard",
  id,
});

export const DeleteObservedHazardCopy =
  (hazardId: HazardId) =>
  (copyId: number): Action => ({
    type: "DeleteObservedHazardCopy",
    hazardId,
    copyId,
  });

export const ChangeHazardDescription =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "ChangeHazardDescription",
    hazardId,
    copyId,
    value,
  });

export const ChangeEnergyLevel =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "ChangeEnergyLevel",
    hazardId,
    copyId,
    value,
  });

export const ToggleIsDirectControlsImplemented =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: O.Option<boolean>): Action => ({
    type: "ToggleIsDirectControlsImplemented",
    hazardId,
    copyId,
    value,
  });

export const SelectedDirectControl =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "SelectedDirectControl",
    hazardId,
    copyId,
    value,
  });

export const RemovedDirectControl =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "RemovedDirectControl",
    hazardId,
    copyId,
    value,
  });

export const ChangeDirectControlsDescription =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "ChangeDirectControlsDescription",
    hazardId,
    copyId,
    value,
  });

export const SelectedNoDirectControlReason =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: O.Option<string>): Action => ({
    type: "SelectedNoDirectControlReason",
    hazardId,
    copyId,
    value,
  });

export const SelectedLimitedControl =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "SelectedLimitedControl",
    hazardId,
    copyId,
    value,
  });

export const RemovedLimitedControl =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "RemovedLimitedControl",
    hazardId,
    copyId,
    value,
  });

export const ChangeLimitedControlsDescription =
  (hazardId: HazardId) =>
  (copyId: number) =>
  (value: string): Action => ({
    type: "ChangeLimitedControlsDescription",
    hazardId,
    copyId,
    value,
  });

export const ShowRecommendedHazardDialog = (): Action => ({
  type: "ShowRecommendedHazardDialog",
});

export const CloseRecommendedHazardDialog = (): Action => ({
  type: "CloseRecommendedHazardDialog",
});

export const ShowError = (
  errorType: HighEnergyTaskSubSectionErrors
): Action => ({
  type: "ShowError",
  errorType,
});

type TaskHazardControl = { id: string; name: string };

export type TaskHazardData = {
  id: HazardId;
  hazardControlConnectorId: string | null;
  observed: boolean;
  description: string;
  energyLevel: string;
  reason: string;
  directControlsImplemented: boolean | null;
  directControls: TaskHazardControl[];
  indirectControls: TaskHazardControl[];
  limitedControls: TaskHazardControl[];
  directControlDescription: string;
  limitedControlDescription: string;
};

export const generateTaskHazardData =
  (hazards: Hazard[]) =>
  (model: Model): TaskHazardData[] =>
    pipe(
      hazards,
      A.chain(hazard =>
        pipe(
          O.fromNullable(model.selectedHazards.get(hazard.id)),
          O.fold(
            () => [
              {
                id: hazard.id,
                hazardControlConnectorId: uuid() as HazardControlConnectorId,
                taskHazardConnectorId: model.taskHazardConnectorId,
                name: getHazardNameOfHazardId(hazards)(hazard.id),
                observed: false,
                description: "",
                energyLevel: "",
                directControlsImplemented: null,
                directControls: [],
                indirectControls: [],
                limitedControls: [],
                directControlDescription: "",
                limitedControlDescription: "",
                reason: "",
              },
            ],
            hazardObservations =>
              pipe(
                hazardObservations,
                M.map(hazardObservation => {
                  const hazardControlConnectorId = pipe(
                    hazardObservation.hazardControlConnectorId,
                    O.fold(
                      () => uuid() as HazardControlConnectorId,
                      thcId => thcId
                    )
                  );
                  return {
                    id: hazard.id,
                    hazardControlConnectorId: hazardControlConnectorId,
                    taskHazardConnectorId: model.taskHazardConnectorId,
                    name: getHazardNameOfHazardId(hazards)(hazard.id),
                    observed: true,
                    description: hazardObservation.description,
                    energyLevel: hazardObservation.energyLevel.raw,
                    directControlsImplemented: O.isSome(
                      hazardObservation.isDirectControlsImplemented
                    )
                      ? hazardObservation.isDirectControlsImplemented.value
                      : null,
                    directControls: pipe(
                      hazardObservation.directControls,
                      S.toArray(ordString),
                      A.map(dcId => ({
                        id: dcId,
                        hazardControlConnectorId: hazardControlConnectorId,
                        name: getHazardControlNameOfControlId(hazards)(dcId),
                      }))
                    ),
                    indirectControls: [],
                    limitedControls: pipe(
                      hazardObservation.limitedControls,
                      S.toArray(ordString),
                      A.map(lcId => ({
                        id: lcId,
                        hazardControlConnectorId: hazardControlConnectorId,
                        name: getHazardControlNameOfControlId(hazards)(lcId),
                      }))
                    ),
                    directControlDescription:
                      hazardObservation.directControlDescription,
                    limitedControlDescription:
                      hazardObservation.limitedControlDescription,
                    reason: pipe(
                      hazardObservation.noDirectControls,
                      O.getOrElse(() => "")
                    ),
                  };
                }),
                M.toArray(ordNumber),
                A.map(Tup.snd)
              )
          )
        )
      )
    );

const directControlsDescriptionRequiredValidation =
  (hazards: Hazard[]) => (hazard: TaskHazardData) =>
    pipe(
      getOtherControlId(hazards)(hazard.id)(ControlType.DIRECT),
      O.fold(
        () => true,
        oId =>
          pipe(
            hazard.directControls,
            A.map(dc => dc.id),
            A.elem(eqString)(oId),
            matchBoolean(
              () => true,
              () => !pipe(hazard.directControlDescription, string.isEmpty)
            )
          )
      )
    );

const limitedControlsDescriptionRequiredValidation =
  (hazards: Hazard[]) => (hazard: TaskHazardData) =>
    pipe(
      getOtherControlId(hazards)(hazard.id)(ControlType.INDIRECT),
      O.fold(
        () => true,
        oId =>
          pipe(
            hazard.limitedControls,
            A.map(lc => lc.id),
            A.elem(eqString)(oId),
            matchBoolean(
              () => true,
              () => !pipe(hazard.limitedControlDescription, string.isEmpty)
            )
          )
      )
    );

const noDirectControlsLimitedControlRequiredCaseValidation = (
  hazard: TaskHazardData
) => {
  const tenantName = getTenantName();
  const UN_CONTROLLED_REASONS = getUncontrolledReasons(tenantName);
  return pipe(
    hazard.reason,
    reason => eqString.equals(reason, UN_CONTROLLED_REASONS[2].label),
    matchBoolean(
      () => true,
      () => pipe(hazard.limitedControls, A.isNonEmpty)
    )
  );
};
const energyLevelIsRequiredForOtherHazardCaseValidation =
  (hazards: Hazard[]) => (hazard: TaskHazardData) =>
    pipe(
      hazards,
      getOtherHazardId,
      O.map(otherHazardId =>
        pipe(
          hazard,
          h => h.id === otherHazardId,
          matchBoolean(
            () => true,
            () => pipe(hazard.energyLevel, energyLevelValidation)
          )
        )
      ),
      O.getOrElse(() => true)
    );

const validateObservedHazardBasedOnControlsImplemented =
  (hazards: Hazard[]) =>
  (observedHazard: TaskHazardData) =>
  (directControlsImplemented: boolean) => {
    return pipe(
      directControlsImplemented,
      matchBoolean(
        () =>
          pipe(
            observedHazard,
            E.fromPredicate(
              h => pipe(h.reason, r => !string.isEmpty(r)),
              () => ({
                type: "form_validation" as const,
                msg: "At least one indirect controls should be selected",
              })
            ),
            E.chain(
              E.fromPredicate(
                noDirectControlsLimitedControlRequiredCaseValidation,
                () => ({
                  type: "form_validation" as const,
                  msg: "When limited controls used is selected on indirect controls, at least one limited controls should be selected",
                })
              )
            ),
            E.chain(
              E.fromPredicate(
                limitedControlsDescriptionRequiredValidation(hazards),
                () => ({
                  type: "form_validation" as const,
                  msg: "Others is selected as a limited control, so description cannot be empty.",
                })
              )
            )
          ),
        () =>
          pipe(
            observedHazard,
            E.fromPredicate(
              h => pipe(h.directControls, A.isNonEmpty),
              () => ({
                type: "form_validation" as const,
                msg: "At least one direct controls should be selected.",
              })
            ),
            E.chain(
              E.fromPredicate(
                directControlsDescriptionRequiredValidation(hazards),
                () => ({
                  type: "form_validation" as const,
                  msg: "Others is selected as a direct control, so description cannot be empty.",
                })
              )
            ),
            E.chain(
              E.fromPredicate(
                limitedControlsDescriptionRequiredValidation(hazards),
                () => ({
                  type: "form_validation" as const,
                  msg: "Others is selected as a limited control, so description cannot be empty.",
                })
              )
            )
          )
      )
    );
  };

export const getTaskHazardIdsWithError =
  (hazards: Hazard[]) =>
  (model: Model): string[] => {
    const observedHazards: TaskHazardData[] = pipe(
      model,
      generateTaskHazardData(hazards),
      A.filter(h => h.observed)
    );

    return pipe(
      observedHazards,
      A.map(observedHazard => ({
        hazardId: observedHazard.id,
        errorState: pipe(
          observedHazard,
          E.fromPredicate(
            energyLevelIsRequiredForOtherHazardCaseValidation(hazards),
            () => ({
              type: "form_validation" as const,
              msg: "Energy level is required and should be at least 500 foot-pounds for observed Other hazard",
            })
          ),
          E.chain(
            flow(
              h => h.directControlsImplemented,
              O.fromNullable,
              O.map(
                validateObservedHazardBasedOnControlsImplemented(hazards)(
                  observedHazard
                )
              ),
              O.getOrElse(
                (): E.Either<eboFormValidationError, TaskHazardData> =>
                  E.left({
                    type: "form_validation" as const,
                    msg: "Observed hazards should indicate direct control implemented status.",
                  })
              )
            )
          )
        ),
      })),
      A.filter(observedHazard => E.isLeft(observedHazard.errorState)),
      A.map(observedHazard => observedHazard.hazardId)
    );
  };

export const validateTaskHazardData =
  (hazards: Hazard[]) =>
  (model: Model): E.Either<eboFormValidationError, TaskHazardData[]> => {
    const observedHazards: TaskHazardData[] = pipe(
      model,
      generateTaskHazardData(hazards),
      A.filter(h => h.observed)
    );

    return pipe(
      observedHazards,
      A.map(observedHazard =>
        pipe(
          observedHazard,
          E.fromPredicate(
            energyLevelIsRequiredForOtherHazardCaseValidation(hazards),
            () => ({
              type: "form_validation" as const,
              msg: "Energy level is required and should be at least 500 foot-pounds for observed Other hazard",
            })
          ),
          E.chain(
            flow(
              h => h.directControlsImplemented,
              O.fromNullable,
              O.map(
                validateObservedHazardBasedOnControlsImplemented(hazards)(
                  observedHazard
                )
              ),
              O.getOrElse(
                (): E.Either<eboFormValidationError, TaskHazardData> =>
                  E.left({
                    type: "form_validation" as const,
                    msg: "Observed hazards should indicate direct control implemented status.",
                  })
              )
            )
          )
        )
      ),
      A.sequence(E.Applicative)
    );
  };

export const toSaveEboInput =
  (tasks: LibraryTask[]) =>
  (hazards: Hazard[]) =>
  (
    model: Model
  ): E.Either<eboFormValidationError, EboHighEnergyTaskConceptInput> => {
    return pipe(
      model,
      generateTaskHazardData(hazards),
      h => ({
        id: model.taskId,
        name: pipe(
          tasks,
          A.findFirst(task => task.id === model.taskId),
          O.map(task => task.name),
          O.getOrElse(() => String(model.taskId))
        ),
        activityId: model.activityId,
        activityName: model.activityName,
        instanceId: model.instanceId,
        taskHazardConnectorId: model.taskHazardConnectorId,
        hazards: h,
      }),
      E.of
    );
  };

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "HazardObserved": {
      if (action.value) {
        const initialObservedHazard = new Map([[0, initialSelectedHazardData]]);

        return [
          {
            ...model,
            error: O.none,
            selectedHazards: pipe(
              model.selectedHazards,
              M.upsertAt(eqHazardId)(action.id, initialObservedHazard)
            ),
          },
          noEffect,
        ];
      } else {
        return [
          {
            ...model,
            error: O.none,
            selectedHazards: pipe(
              model.selectedHazards,
              M.deleteAt(eqHazardId)(action.id)
            ),
          },
          noEffect,
        ];
      }
    }
    case "CopyObservedHazard": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.id, hazards =>
              pipe(
                hazards,
                shouldAddNewHazard,
                O.fold(
                  () => hazards, // Should not add a new hazard so return the current hazards
                  () =>
                    pipe(
                      hazards,
                      generateNewDuplicateHazardIdx,
                      O.map(idx =>
                        pipe(
                          hazards,
                          M.upsertAt(eqNumber)(idx, initialSelectedHazardData)
                        )
                      ),
                      O.getOrElse(() => hazards)
                    )
                )
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "DeleteObservedHazardCopy": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards => {
              return pipe(hazards, M.deleteAt(eqNumber)(action.copyId));
            }),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ChangeHazardDescription": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  description: action.value,
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ChangeEnergyLevel": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  energyLevel: updateFormField<
                    t.Errors,
                    string,
                    Option<number>
                  >(optionFromString(tt.NumberFromString).decode)(action.value),
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ToggleIsDirectControlsImplemented": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  isDirectControlsImplemented: action.value,
                  directControls: new Set<string>(),
                  directControlDescription: "",
                  noDirectControls: O.none,
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "SelectedDirectControl": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  directControls: pipe(
                    hazard.directControls,
                    S.insert(eqString)(action.value)
                  ),
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "RemovedDirectControl": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  directControls: pipe(
                    hazard.directControls,
                    S.remove(eqString)(action.value)
                  ),
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ChangeDirectControlsDescription": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  directControlDescription: action.value,
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "SelectedNoDirectControlReason": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  noDirectControls: action.value,
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "SelectedLimitedControl": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  limitedControls: pipe(
                    hazard.limitedControls,
                    S.insert(eqString)(action.value)
                  ),
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "RemovedLimitedControl": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  limitedControls: pipe(
                    hazard.limitedControls,
                    S.remove(eqString)(action.value)
                  ),
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ChangeLimitedControlsDescription": {
      return [
        {
          ...model,
          error: O.none,
          selectedHazards: pipe(
            model.selectedHazards,
            M.modifyAt(eqHazardId)(action.hazardId, hazards =>
              pipe(
                hazards,
                M.modifyAt(eqNumber)(action.copyId, hazard => ({
                  ...hazard,
                  limitedControlDescription: action.value,
                })),
                O.getOrElse(() => hazards)
              )
            ),
            O.getOrElse(() => model.selectedHazards)
          ),
        },
        noEffect,
      ];
    }
    case "ShowRecommendedHazardDialog": {
      return [
        {
          ...model,
          error: O.none,
          recommendedHazardDialog: O.some(true),
        },
        noEffect,
      ];
    }
    case "CloseRecommendedHazardDialog": {
      return [
        {
          ...model,
          error: O.none,
          recommendedHazardDialog: O.some(false),
        },
        noEffect,
      ];
    }
    case "ShowError": {
      return [{ ...model, error: O.some(action.errorType) }, scrollTopEffect()];
    }
  }
};

const applicabilityOrder = [
  ApplicabilityLevel.ALWAYS,
  ApplicabilityLevel.MOSTLY,
  ApplicabilityLevel.RARELY,
  ApplicabilityLevel.NEVER,
];

export const isOtherHazard = (hazard: Hazard) =>
  pipe(hazard.name, hazardName =>
    eqString.equals(hazardName, OTHER_HAZARD_NAME)
  );

const sortHazards =
  (taskId: LibraryTaskId) =>
  (selectedHazards: SelectedHazards) =>
  (hazards: Hazard[]) => {
    const isSelected = (hazardId: HazardId) =>
      pipe(selectedHazards, M.member(eqHazardId)(hazardId));

    const taskApplicabilityOrder = (hazard: Hazard) =>
      pipe(
        hazard.taskApplicabilityLevels,
        A.findFirst(level => eqString.equals(level.taskId, taskId)),
        O.map(level => applicabilityOrder.indexOf(level.applicabilityLevel))
      );

    return hazards.sort((a: Hazard, b: Hazard): number => {
      // If one hazard is named as Other, prioritize the other one
      if (isOtherHazard(a)) return 1;
      if (isOtherHazard(b)) return -1;
      // If one hazard is selected and other is not, prioritize the selected hazard
      if (isSelected(a.id) && !isSelected(b.id)) return -1;
      if (!isSelected(a.id) && isSelected(b.id)) return 1;

      // if both hazards are selected or not selected, apply usual sorting logic based on task applicabilityLevel
      const taskApplicabilityOrderA = taskApplicabilityOrder(a);
      const taskApplicabilityOrderB = taskApplicabilityOrder(b);
      if (
        O.isSome(taskApplicabilityOrderA) &&
        O.isSome(taskApplicabilityOrderB)
      ) {
        if (taskApplicabilityOrderA.value < taskApplicabilityOrderB.value)
          return -1;
        if (taskApplicabilityOrderA.value > taskApplicabilityOrderB.value)
          return -1;
      }

      return 0;
    });
  };

export type Props = ChildProps<Model, Action> & {
  tasks: LibraryTask[];
  hazards: Hazard[];
  saveEbo: () => void;
  isReadOnly: boolean;
  originalTaskNames: Map<LibraryTaskId, string>;
};

const createHazardsWithSavedNames = (
  libraryHazards: Hazard[],
  savedHazardNames: Map<HazardId, string>,
  savedControlNames: Map<string, string>
): Hazard[] => {
  return pipe(
    libraryHazards,
    A.map(hazard => ({
      ...hazard,
      name: savedHazardNames.get(hazard.id) || hazard.name,
      controls: hazard.controls.map(control => ({
        ...control,
        name: savedControlNames.get(control.id) || control.name,
      })),
    }))
  );
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, hazards, isReadOnly } = props;

  const task = useMemo(() => {
    return pipe(
      props.tasks,
      A.filter(ta => ta.id === model.taskId),
      A.head
    );
  }, [props.tasks, model.taskId]);

  const taskName = useMemo(() => {
    const originalTaskName = props.originalTaskNames.get(model.taskId);
    if (originalTaskName) {
      return originalTaskName;
    }

    return pipe(
      task,
      O.map(t => t.name),
      O.getOrElse(() => String(model.taskId))
    );
  }, [props.originalTaskNames, task, model.taskId]);

  const activity = useMemo(() => {
    return pipe(
      task,

      O.chain(ta =>
        A.head(Array.isArray(ta.activitiesGroups) ? ta.activitiesGroups : [])
      )
    );
  }, [task]);

  const closeRecommendedHazardDialog = () =>
    flow(CloseRecommendedHazardDialog, dispatch);

  const recommendedHazards = useMemo(
    () => getRecommendedHazards(hazards, model.selectedHazards, model.taskId),
    [model.recommendedHazardDialog]
  );

  const hazardsWithSavedNames = useMemo(
    () =>
      createHazardsWithSavedNames(
        hazards,
        model.savedHazardNames,
        model.savedControlNames
      ),
    [hazards, model.savedHazardNames, model.savedControlNames]
  );

  const sortedHazards = useMemo(
    () =>
      pipe(
        hazardsWithSavedNames,
        sortHazards(model.taskId)(model.selectedHazards)
      ),
    [hazardsWithSavedNames, task]
  );

  return (
    <StepLayout>
      {O.isSome(task) && O.isSome(activity) && (
        <div className="flex flex-col gap-3">
          <span className="font-semibold text-xl text-neutral-shade-100">
            {model.activityName}
          </span>
          <TaskCard
            title={taskName}
            risk={task.value.riskLevel}
            showRiskInformation={false}
            showRiskText={false}
            withLeftBorder={false}
          />
        </div>
      )}
      {O.isSome(model.error) && (
        <div className="text-system-error-40 font-semibold text-sm">
          {highEnergyTaskSubSectionErrorTexts(model.error.value)}
        </div>
      )}
      {sortedHazards.map(hazard => (
        <HazardWrapper
          key={hazard.id}
          hazard={hazard}
          observationsForHazard={O.fromNullable(
            model.selectedHazards.get(hazard.id)
          )}
          dispatch={dispatch}
          closeDropDownOnOutsideClick={false}
          isReadOnly={isReadOnly}
        />
      ))}
      {O.isSome(model.recommendedHazardDialog) &&
        model.recommendedHazardDialog.value && (
          <Dialog
            header={
              <RecommendedHazardDialogHeader
                onClose={closeRecommendedHazardDialog()}
              />
            }
            footer={
              <RecommendedHazardDialogFooter
                onSubmit={closeRecommendedHazardDialog()}
              />
            }
          >
            <div className="flex flex-col gap-2 pr-4">
              {recommendedHazards.map(hazard => (
                <HazardWrapper
                  key={hazard.id}
                  hazard={hazard}
                  observationsForHazard={O.fromNullable(
                    model.selectedHazards.get(hazard.id)
                  )}
                  dispatch={dispatch}
                  closeDropDownOnOutsideClick={false}
                  isReadOnly={isReadOnly}
                />
              ))}
            </div>
          </Dialog>
        )}
    </StepLayout>
  );
}

export default View;

const RecommendedHazardDialogHeader = ({
  onClose,
}: {
  onClose: () => void;
}): JSX.Element => (
  <div className="flex flex-col gap-2">
    <div className="flex flex-row justify-between">
      <SectionHeading className="text-xl font-semibold">
        Recommended High Energy Hazards
      </SectionHeading>
      <ButtonIcon iconName="close_big" onClick={onClose} />
    </div>
    <p>{messages.RecommendedHazardModalSubTitle}</p>
  </div>
);

const RecommendedHazardDialogFooter = ({
  onSubmit,
}: {
  onSubmit: () => void;
}): JSX.Element => (
  <div className="flex flex-row justify-end gap-2">
    <ButtonPrimary label="Confirm updates" onClick={onSubmit} />
  </div>
);
