import type {
  ControlSelection,
  Hazard,
  HazardControl,
  HazardControlId,
  HazardId,
  Jsb,
  LibraryTask,
} from "@/api/codecs";
import type { SaveJobSafetyBriefingInput } from "@/api/generated/types";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/lib/Option";
import type { StepSnapshot } from "../Utils";
import * as A from "fp-ts/lib/Array";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import * as M from "fp-ts/lib/Map";
import { match as matchBoolean } from "fp-ts/boolean";
import { constant, flow, identity, pipe } from "fp-ts/lib/function";
import { useCallback, useMemo } from "react";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Ord as OrdString } from "fp-ts/lib/string";
import {
  eqControlSelectionById,
  eqHazardControlId,
  eqHazardId,
  ordControlSelectionById,
  ordHazardControlId,
  ordHazardId,
} from "@/api/codecs";
import { MultiSelect } from "../Basic/MultiSelect";
import StepLayout from "../StepLayout";
import { FieldGroup } from "../../shared/FieldGroup";
import { Checkbox } from "../Basic/Checkbox";
import { snapshotMap } from "../Utils";

export type Model = {
  hazards: Map<
    HazardId,
    {
      controlIds: Set<HazardControlId>;
      controlSelections: Set<ControlSelection>;
    }
  >;
  notes: string;
};

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    hazards: pipe(
      model.hazards,
      M.map(({ controlIds, controlSelections }) => ({
        controlIds: S.toArray(ordHazardControlId)(controlIds),
        controlSelections: S.toArray(ordControlSelectionById)(
          controlSelections
        ),
      })),
      snapshotMap
    ),
    notes: model.notes,
  };
}

export const init = (jsb: Option<Jsb>): Model => ({
  hazards: pipe(
    jsb,
    O.chain(j => j.controlAssessmentSelections),
    O.fold(
      () =>
        new Map<
          HazardId,
          {
            controlIds: Set<HazardControlId>;
            controlSelections: Set<ControlSelection>;
          }
        >(),
      cass =>
        pipe(
          cass,
          A.reduce(
            new Map<
              HazardId,
              {
                controlIds: Set<HazardControlId>;
                controlSelections: Set<ControlSelection>;
              }
            >(),
            (acc, cas) => {
              // Ensure that each hazardId has a Map entry
              const hazardId = cas.hazardId;
              const existing = acc.get(hazardId) ?? {
                controlIds: S.empty,
                controlSelections: S.empty,
              };

              const updatedControlIds = pipe(
                cas.controlIds,
                O.fromNullable, // Convert null or undefined to O.none
                O.fold(
                  () => existing.controlIds, // If it's null or None, keep existing controlIds
                  ids =>
                    S.union(eqHazardControlId)(existing.controlIds)(
                      S.fromArray(eqHazardControlId)(ids)
                    ) // Union with new controlIds
                )
              );

              const updatedControlSelections = pipe(
                cas.controlSelections,
                O.fromNullable, // Convert null or undefined to O.none
                O.fold(
                  () => existing.controlSelections, // If it's null or None, keep existing controlSelections
                  selections =>
                    S.union(eqControlSelectionById)(existing.controlSelections)(
                      S.fromArray(eqControlSelectionById)(selections)
                    ) // Union with new controlSelections
                )
              );

              acc.set(hazardId, {
                controlIds: updatedControlIds,
                controlSelections: updatedControlSelections,
              });
              return acc;
            }
          )
        )
    )
  ),
  notes: pipe(
    jsb,
    O.chain(j => j.hazardsAndControlsNotes),
    O.getOrElse(() => "")
  ),
});

// needed for initializing control selections to "all selected" default state
// but we should'n add new selections if it has been touched
export const preselectControls =
  (hazards: Hazard[]) =>
  (model: Model): Model => {
    // Iterate over the hazards and preselect controls for those that are not yet added
    // hazards list should represent selected tasks and site conditions.
    // As it is not an HazardControlID[] anymore, after generating hs
    // it should be filtered through with respect to selected items.
    const updatedHazards = hazards.reduce((acc, h) => {
      // Only preselect controls for hazards that are not already present in the model
      if (!M.member(eqHazardId)(h.id)(model.hazards)) {
        const controlIds = pipe(
          h.controls,
          A.map(c => c.id),
          S.fromArray(eqHazardControlId)
        );

        const controlSelections = pipe(
          h.controls,
          A.map(c => ({
            id: c.id,
            selected: true,
            recommended: true,
            name: c.name,
          })),
          S.fromArray(eqControlSelectionById)
        );

        // Update the hazard entry with controlIds and controlSelections
        acc.set(h.id, {
          controlIds,
          controlSelections,
        });
      }
      return acc;
    }, new Map<HazardId, { controlIds: Set<HazardControlId>; controlSelections: Set<ControlSelection> }>(model.hazards));

    // Return the updated model with the newly preselected controls
    return {
      ...model,
      hazards: updatedHazards,
    };
  };

export const toSaveJsbInput =
  (hazards: Hazard[], tasks: LibraryTask[]) =>
  (model: Model): SaveJobSafetyBriefingInput => {
    const hazardById = new Map(
      hazards.map(hazard => [hazard.id, hazard.name] as const)
    );

    const getControlNames = pipe(
      tasks,
      A.chain(t => t.hazards),
      A.chain(h => h.controls),
      A.uniq(eqHazardControlById)
    );

    const controlById = new Map(
      getControlNames.map(control => [control.id, control.name] as const)
    );

    const controlAssessmentSelections = pipe(
      model.hazards,
      M.toArray(ordHazardId),
      A.map(([hazardId, controls]) => ({
        hazardId,
        name: hazardById.get(hazardId) ?? "",
        controlIds: pipe(
          controls.controlIds, // Use controlIds from the object
          S.toArray(ordHazardControlId) // Convert Set<HazardControlId> to array
        ),
        controlSelections: pipe(
          controls.controlSelections, // Use controlSelections from the object
          S.toArray(ordControlSelectionById), // Convert Set<ControlSelection> to array
          A.map(controlSelection => ({
            ...controlSelection,
            name: controlById.get(controlSelection.id) ?? "",
          }))
        ),
      }))
    );

    return {
      controlAssessmentSelections,
      hazardsAndControlsNotes: model.notes,
    };
  };

export type Action =
  | {
      type: "ControlSelected";
      hazardId: HazardId;
      controlId: HazardControlId;
    }
  | {
      type: "ControlRemoved";
      hazardId: HazardId;
      controlId: HazardControlId;
    }
  | {
      type: "ManyControlsSelected";
      hazardId: HazardId;
      controlIds: HazardControlId[];
    }
  | {
      type: "NotesChanged";
      notes: string;
    }
  | {
      type: "UnselectManyControlsSelected";
      hazardId: HazardId;
      controlIds: HazardControlId[];
    };

export const ControlSelected =
  (hazardId: HazardId) =>
  (controlId: HazardControlId): Action => ({
    type: "ControlSelected",
    hazardId,
    controlId,
  });

export const ControlRemoved =
  (hazardId: HazardId) =>
  (controlId: HazardControlId): Action => ({
    type: "ControlRemoved",
    hazardId,
    controlId,
  });

export const ManyControlsSelected =
  (hazardId: HazardId) =>
  (controlIds: HazardControlId[]): Action => ({
    type: "ManyControlsSelected",
    hazardId,
    controlIds,
  });

export const NotesChanged = (notes: string): Action => ({
  type: "NotesChanged",
  notes,
});

export const UnselectManyControlsSelected =
  (hazardId: HazardId) =>
  (controlIds: HazardControlId[]): Action => ({
    type: "UnselectManyControlsSelected",
    hazardId,
    controlIds,
  });

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "ControlSelected": {
      const hazard = M.lookup(eqHazardId)(action.hazardId)(model.hazards);
      if (O.isNone(hazard)) {
        return model; // If no hazard is found, return the model unchanged
      }

      const { controlIds, controlSelections } = hazard.value;

      // Update controlSelections: check if the controlId is already selected, if not, add it
      const updatedControlSelections = pipe(
        controlSelections,
        S.toArray(ordControlSelectionById),
        controls =>
          pipe(
            controls,
            A.map(cs => cs.id),
            A.elem(eqHazardControlId)(action.controlId),
            matchBoolean(
              () =>
                pipe(
                  controls,
                  A.append({
                    id: action.controlId,
                    selected: true,
                    recommended: false,
                  })
                ),
              () =>
                pipe(
                  controls,
                  A.map(controlSelection => {
                    if (controlSelection.id !== action.controlId)
                      return controlSelection;
                    return { ...controlSelection, selected: true };
                  })
                )
            )
          ),
        S.fromArray(ordControlSelectionById)
      );

      return {
        ...model,
        hazards: pipe(
          model.hazards,
          M.upsertAt(eqHazardId)(action.hazardId, {
            controlIds,
            controlSelections: updatedControlSelections,
          })
        ),
      };
    }

    case "ControlRemoved": {
      const hazard = M.lookup(eqHazardId)(action.hazardId)(model.hazards);
      if (O.isNone(hazard)) {
        return model; // If no hazard is found, return the model unchanged
      }

      const { controlIds, controlSelections } = hazard.value;

      // Update controlIds: remove the controlId from the hazard's controlIds set
      const updatedControlIds = S.remove(eqHazardControlId)(action.controlId)(
        controlIds
      );

      // Update controlSelections: set the selected property of the matching control selection to false
      const updatedControlSelections = pipe(
        controlSelections,
        S.map(eqControlSelectionById)(controlSelection => {
          if (controlSelection.id !== action.controlId) return controlSelection;
          return { ...controlSelection, selected: false };
        })
      );

      return {
        ...model,
        hazards: pipe(
          model.hazards,
          M.upsertAt(eqHazardId)(action.hazardId, {
            controlIds: updatedControlIds,
            controlSelections: updatedControlSelections,
          })
        ),
      };
    }

    case "ManyControlsSelected": {
      const hazard = M.lookup(eqHazardId)(action.hazardId)(model.hazards);
      if (O.isNone(hazard)) {
        return model; // If no hazard is found, return the model unchanged
      }

      const { controlIds, controlSelections } = hazard.value;

      // Update controlSelections: add multiple controlIds, or update their selected state to true
      const updatedControlSelections = pipe(
        controlSelections,
        S.toArray(ordControlSelectionById),
        controls =>
          pipe(
            action.controlIds,
            A.reduce(controls, (result, controlId) => {
              if (result.some(cs => cs.id === controlId)) {
                return pipe(
                  result,
                  A.map(cs =>
                    cs.id === controlId ? { ...cs, selected: true } : cs
                  )
                );
              } else {
                return pipe(
                  result,
                  A.append({
                    id: controlId,
                    selected: true,
                    recommended: false,
                  })
                );
              }
            })
          ),
        S.fromArray(ordControlSelectionById)
      );

      return {
        ...model,
        hazards: pipe(
          model.hazards,
          M.upsertAt(eqHazardId)(action.hazardId, {
            controlIds,
            controlSelections: updatedControlSelections,
          })
        ),
      };
    }

    case "UnselectManyControlsSelected": {
      const hazard = M.lookup(eqHazardId)(action.hazardId)(model.hazards);
      if (O.isNone(hazard)) {
        return model; // If no hazard is found, return the model unchanged
      }

      const { controlIds, controlSelections } = hazard.value;

      // Update controlSelections: set selected to false for multiple controls
      const updatedControlSelections = pipe(
        controlSelections,
        S.toArray(ordControlSelectionById),
        controls =>
          pipe(
            action.controlIds,
            A.reduce(controls, (result, controlId) => {
              return pipe(
                result,
                A.map(cs =>
                  cs.id === controlId ? { ...cs, selected: false } : cs
                )
              );
            })
          ),
        S.fromArray(ordControlSelectionById)
      );

      return {
        ...model,
        hazards: pipe(
          model.hazards,
          M.upsertAt(eqHazardId)(action.hazardId, {
            controlIds,
            controlSelections: updatedControlSelections,
          })
        ),
      };
    }

    case "NotesChanged":
      return {
        ...model,
        notes: action.notes,
      };

    default:
      return model;
  }
};

export type Props = ChildProps<Model, Action> & {
  hazards: Hazard[];
  tasks: LibraryTask[];
  isReadOnly: boolean;
};

const eqHazardControlById = Eq.contramap((c: HazardControl) => c.id)(
  eqHazardControlId
);

const ordHazardControlByName = Ord.contramap((c: HazardControl) => c.name)(
  OrdString
);

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const allControls = useMemo(
    () =>
      pipe(
        props.tasks,
        A.chain(t => t.hazards),
        A.chain(h => h.controls),
        A.uniq(eqHazardControlById)
      ),
    [props.tasks]
  );

  // precompute options for the controls multiselects
  // both multiselects share the same selection set, but use different options source
  // this ensures the uniqueness of the selected ids
  const hazards = useMemo(
    () =>
      pipe(
        props.hazards,
        A.map(h => ({
          id: h.id,
          name: h.name,
          recommendedControls: pipe(
            h.controls,
            A.map(c => ({
              value: c.id,
              label: c.name,
            }))
          ),
          otherControls: pipe(
            allControls,
            A.filter(control => h.controls.every(c => c.id !== control.id)),
            A.sort(ordHazardControlByName),
            A.map(c => ({
              value: c.id,
              label: c.name,
            }))
          ),
        }))
      ),
    [props.hazards, allControls]
  );

  const selectedControlIds = useCallback(
    (hazardId: HazardId) => {
      const hazard = model.hazards.get(hazardId);
      if (!hazard) return [];

      const selectedIds: HazardControlId[] = [];
      hazard.controlSelections.forEach(controlSelection => {
        if (controlSelection.selected) {
          selectedIds.push(controlSelection.id);
        }
      });
      return selectedIds;
    },
    [model.hazards]
  );

  // check if a set of recommended control ids is a subset of the selected control ids for a hazard
  // this is used to determine if the "all recommended" checkbox should be checked
  const allRecommendedSelected = useCallback(
    (hazardId: HazardId) =>
      pipe(
        O.Do,
        O.bind("recommended", () =>
          pipe(
            props.hazards,
            A.findFirst(h => h.id === hazardId),
            O.map(h =>
              pipe(
                h.controls,
                A.map(c => c.id),
                S.fromArray(eqHazardControlId)
              )
            )
          )
        ),
        O.bind("selected", () =>
          pipe(
            model.hazards,
            M.lookup(eqHazardId)(hazardId),
            O.map(({ controlSelections }) =>
              pipe(
                controlSelections,
                S.toArray(ordControlSelectionById),
                A.filter(controlSelection => controlSelection.selected), // Filter by selected
                A.map(controlSelection => controlSelection.id), // Get the ids of selected controls
                S.fromArray(eqHazardControlId) // Convert to Set<HazardControlId>
              )
            )
          )
        ),
        O.map(
          ({ recommended, selected }) =>
            S.isSubset(eqHazardControlId)(selected)(recommended) // Check if selected is a subset of recommended
        ),
        O.getOrElse(() => false)
      ),
    [model.hazards, props.hazards]
  );

  const nonRecommendedSelectedControlIds = useCallback(
    (hazardId: HazardId, selectedIds) =>
      pipe(
        hazards,
        A.findFirst(h => h.id === hazardId),
        O.match(
          () => [],
          h => h.otherControls.map(c => c.value)
        ),
        otherControlIds =>
          A.filter((sId: HazardControlId) => otherControlIds.includes(sId))(
            selectedIds
          ),
        A.sort(ordHazardControlId)
      ),
    [hazards]
  );

  return (
    <StepLayout>
      {hazards.map(hazard => {
        return (
          <FieldGroup key={hazard.id} legend={hazard.name}>
            <Checkbox
              checked={allRecommendedSelected(hazard.id)}
              disabled={isReadOnly}
              onClick={
                allRecommendedSelected(hazard.id)
                  ? flow(
                      constant(hazard.recommendedControls.map(c => c.value)),
                      UnselectManyControlsSelected(hazard.id),
                      dispatch
                    )
                  : flow(
                      constant(hazard.recommendedControls.map(c => c.value)),
                      ManyControlsSelected(hazard.id),
                      dispatch
                    )
              }
            >
              Select all recommended controls
            </Checkbox>
            <MultiSelect
              label="Recommended controls"
              options={hazard.recommendedControls}
              renderLabel={identity}
              optionKey={identity}
              selected={selectedControlIds(hazard.id)}
              disabled={isReadOnly}
              onSelected={flow(ControlSelected(hazard.id), dispatch)}
              onRemoved={flow(ControlRemoved(hazard.id), dispatch)}
            />

            <MultiSelect
              label="Other controls"
              typeahead
              options={hazard.otherControls}
              renderLabel={identity}
              optionKey={identity}
              selected={nonRecommendedSelectedControlIds(
                hazard.id,
                selectedControlIds(hazard.id)
              )}
              disabled={isReadOnly}
              onSelected={flow(ControlSelected(hazard.id), dispatch)}
              onRemoved={flow(ControlRemoved(hazard.id), dispatch)}
            />
          </FieldGroup>
        );
      })}

      <FieldGroup legend="Additional Information">
        <textarea
          className="w-full h-24 p-2 border-solid border-[1px] border-brand-gray-40 rounded"
          value={model.notes}
          disabled={isReadOnly}
          onChange={e => pipe(e.target.value, NotesChanged, dispatch)}
        />
      </FieldGroup>
    </StepLayout>
  );
}
