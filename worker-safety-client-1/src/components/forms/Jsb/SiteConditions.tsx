import type {
  LibrarySiteCondition,
  LibrarySiteConditionId,
  ProjectLocationId,
} from "@/api/codecs";
import type {
  CreateSiteConditionInput,
  SaveJobSafetyBriefingInput,
} from "@/api/generated/types";
import type { Option } from "fp-ts/lib/Option";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { StepSnapshot } from "../Utils";
import { CaptionText, SectionHeading } from "@urbint/silica";
import * as A from "fp-ts/lib/Array";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import { constant, flow, pipe } from "fp-ts/lib/function";
import { useMemo } from "react";
import { isNone } from "fp-ts/lib/Option";
import {
  eqLibrarySiteConditionId,
  ordLibrarySiteConditionId,
} from "@/api/codecs";
import StepLayout from "../StepLayout";
import { TagCard } from "../Basic/TagCard";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import { Checkbox } from "../Basic/Checkbox";
import { Dialog } from "../Basic/Dialog";

export type Model = {
  recommendedIds: Set<LibrarySiteConditionId>;
  selectedIds: Set<LibrarySiteConditionId>;
  dialog: Option<Set<LibrarySiteConditionId>>;
  relevantIds: Option<Set<LibrarySiteConditionId>>;
};

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    recommendedIds: S.toArray(ordLibrarySiteConditionId)(model.recommendedIds),
    selectedIds: S.toArray(ordLibrarySiteConditionId)(model.selectedIds),
  };
}

export const toSaveJsbInput =
  (siteConditionTasks: LibrarySiteCondition[]) =>
  (model: Model): SaveJobSafetyBriefingInput => {
    const getSiteConditionNameById = new Map(
      siteConditionTasks?.map(
        siteConditionTask =>
          [siteConditionTask.id, siteConditionTask.name] as const
      )
    );

    return {
      siteConditionSelections: S.toArray(ordLibrarySiteConditionId)(
        model.recommendedIds
      ).map(id => ({
        id,
        name: getSiteConditionNameById.get(id) ?? "",
        recommended: true, // redundant property. It's always true because if it's not recommended, it's not saved.
        selected: S.elem(eqLibrarySiteConditionId)(id)(model.selectedIds),
      })),
    };
  };

// relevant site conditions depend on the selected date
// the intention is to reinitialize the site conditions every time the date changes
export const init = (
  selectedSiteConditionIds: Option<LibrarySiteConditionId[]>,
  relevantSiteConditionIds: Option<LibrarySiteConditionId[]>
): Model => {
  const selectedIdsSet = pipe(
    selectedSiteConditionIds,
    O.map(S.fromArray(eqLibrarySiteConditionId))
  );
  const relevantIdsSet = pipe(
    relevantSiteConditionIds,
    O.map(S.fromArray(eqLibrarySiteConditionId))
  );

  const includeRelevantSiteConditions = (ids: Set<LibrarySiteConditionId>) =>
    pipe(
      relevantIdsSet,
      O.fold(() => ids, S.union(eqLibrarySiteConditionId)(ids))
    );

  return {
    selectedIds: pipe(
      // initialize selection with the selected site conditions from the JSB
      selectedIdsSet,
      // if there are no selected site conditions in the JSB,
      // preselect all relevant site conditions
      O.alt(() => relevantIdsSet),
      // if there are no selected or relevant site conditions, initialize with an empty set
      O.getOrElse(() => new Set<LibrarySiteConditionId>())
    ),
    // recommended ids determine which site conditions are displayed on the page
    recommendedIds: pipe(
      selectedIdsSet,
      // if there are site conditions selected in the JSB, combine them with currently relevant site conditions
      // to display site conditions from both sets
      O.map(includeRelevantSiteConditions),
      // if there are no site conditions selected in the JSB, display only relevant site conditions
      O.alt(() => relevantIdsSet),
      // if there are no relevant site conditions, initialize with an empty set (no side conditions with be displayed by initially)
      O.getOrElse(() => new Set<LibrarySiteConditionId>())
    ),
    relevantIds: relevantIdsSet,
    dialog: O.none,
  };
};
export type Action =
  | {
      type: "SiteConditionToggled";
      id: LibrarySiteConditionId;
    }
  | {
      type: "SiteConditionToggledAll";
      ids: LibrarySiteConditionId[];
    }
  | {
      type: "AddSiteConditionsOpened";
      ids: Set<LibrarySiteConditionId>;
    }
  | {
      type: "AddSiteConditionsClosed";
      ids: Option<Set<LibrarySiteConditionId>>;
    }
  | {
      type: "AddSiteConditionsToggled";
      id: LibrarySiteConditionId;
    };

export const SiteConditionToggled = (id: LibrarySiteConditionId): Action => ({
  type: "SiteConditionToggled",
  id,
});

export const AddSiteConditionsOpened = (
  ids: Set<LibrarySiteConditionId>
): Action => ({
  type: "AddSiteConditionsOpened",
  ids,
});

export const AddSiteConditionsClosed = (
  ids: Option<Set<LibrarySiteConditionId>>
): Action => ({
  type: "AddSiteConditionsClosed",
  ids,
});

export const AddSiteConditionsToggled = (
  id: LibrarySiteConditionId
): Action => ({
  type: "AddSiteConditionsToggled",
  id,
});

export const SiteConditionToggledAll = (
  ids: LibrarySiteConditionId[]
): Action => ({
  type: "SiteConditionToggledAll",
  ids,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "SiteConditionToggled":
      return {
        ...model,
        selectedIds: S.toggle(eqLibrarySiteConditionId)(action.id)(
          model.selectedIds
        ),
      };

    case "AddSiteConditionsOpened":
      return {
        ...model,
        dialog: O.some(action.ids),
      };

    case "AddSiteConditionsClosed":
      return {
        ...model,
        recommendedIds: pipe(
          action.ids,
          O.getOrElse(() => model.recommendedIds)
        ),
        selectedIds: pipe(
          action.ids,
          O.fold(
            () => model.selectedIds, // fallback to the previous selection if the dialog was closed without saving
            flow(
              S.difference(eqLibrarySiteConditionId)(model.recommendedIds), // this gives us the ids that were added in the dialog
              S.union(eqLibrarySiteConditionId)(model.selectedIds) // combine them with the previous selection
            )
          )
        ),
        dialog: O.none,
      };

    case "AddSiteConditionsToggled":
      return {
        ...model,
        dialog: pipe(
          model.dialog,
          O.map(ids => S.toggle(eqLibrarySiteConditionId)(action.id)(ids))
        ),
      };
    case "SiteConditionToggledAll": {
      return {
        ...model,
        selectedIds: S.isEmpty(model.selectedIds)
          ? pipe(action.ids, S.fromArray(eqLibrarySiteConditionId))
          : new Set<LibrarySiteConditionId>(),
      };
    }
  }
};

export type Props = ChildProps<Model, Action> & {
  siteConditions: LibrarySiteCondition[];
  isReadOnly: boolean;
  locationId: Option<ProjectLocationId>;
  saveSiteCondition: (a: CreateSiteConditionInput) => void;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const cancelDialog = flow(
    constant(O.none),
    AddSiteConditionsClosed,
    dispatch
  );

  const saveDialog = flow(
    constant(model.dialog),
    AddSiteConditionsClosed,
    dispatch
  );

  const displayedSiteConditions = useMemo(
    () =>
      props.siteConditions.filter(sc =>
        S.elem(eqLibrarySiteConditionId)(sc.id)(model.recommendedIds)
      ),
    [props.siteConditions, model.recommendedIds]
  );

  const areAllOptionsSelected = useMemo(
    () =>
      pipe(
        displayedSiteConditions,
        A.map(sc => sc.id),
        S.fromArray(eqLibrarySiteConditionId),
        S.isSubset(eqLibrarySiteConditionId)(model.selectedIds)
      ),
    [displayedSiteConditions, model.selectedIds]
  );

  const mapSiteConditionToCreateSiteConditionInput = (
    ids: Set<LibrarySiteConditionId>
  ): Option<CreateSiteConditionInput[]> =>
    pipe(
      props.locationId,
      O.map(locationId =>
        pipe(
          ids,
          S.difference(eqLibrarySiteConditionId)(model.recommendedIds),
          S.toArray(ordLibrarySiteConditionId),
          A.filterMap(id =>
            pipe(
              props.siteConditions,
              A.findFirst(sc => sc.id === id)
            )
          ),
          A.map(sc => ({
            locationId: locationId,
            librarySiteConditionId: sc.id,
            hazards: pipe(
              sc.hazards,
              A.map(h => ({
                libraryHazardId: h.id,
                isApplicable: h.isApplicable,
                controls: pipe(
                  h.controls,
                  A.map(c => ({
                    libraryControlId: c.id,
                    isApplicable: c.isApplicable,
                  }))
                ),
              }))
            ),
          }))
        )
      )
    );

  return (
    <div className="w-full">
      <div className="flex flex-row justify-between">
        <SectionHeading className="text-xl font-semibold">
          Add Site Conditions
        </SectionHeading>
        {!isReadOnly && (
          <ButtonSecondary
            label="Add Site Conditions"
            iconStart="plus_circle_outline"
            onClick={flow(
              constant(model.recommendedIds),
              AddSiteConditionsOpened,
              dispatch
            )}
          />
        )}
      </div>

      <CaptionText className="text-sm font-normal mb-4">
        Review the site conditions below and see if they apply to your location.
      </CaptionText>

      <StepLayout>
        {displayedSiteConditions?.length > 0 && (
          <Checkbox
            className="w-full gap-4"
            labelClassName="w-full"
            checked={areAllOptionsSelected}
            disabled={isReadOnly}
            onClick={flow(
              constant(displayedSiteConditions),
              A.map(sc => sc.id),
              SiteConditionToggledAll,
              dispatch
            )}
          >
            <span className="font-semibold text-base">All Site Conditions</span>
          </Checkbox>
        )}
        {displayedSiteConditions.map(sc => (
          <div key={sc.id} className="flex w-full">
            <Checkbox
              className="w-full gap-4"
              labelClassName="w-full"
              checked={model.selectedIds.has(sc.id)}
              disabled={isReadOnly}
              onClick={flow(constant(sc.id), SiteConditionToggled, dispatch)}
            >
              <TagCard className="border-data-blue-30">
                <span className="font-semibold">
                  {sc.name}
                  {isNone(sc.archivedAt) ? "" : " (Archived)"}
                </span>
              </TagCard>
            </Checkbox>
          </div>
        ))}
      </StepLayout>
      {O.isSome(model.dialog) && (
        <Dialog
          header={<DialogHeader onClose={cancelDialog} />}
          footer={
            <DialogFooter
              onSave={flow(
                constant(model.dialog.value),
                mapSiteConditionToCreateSiteConditionInput,
                O.map(A.map(props.saveSiteCondition)),
                saveDialog
              )}
              onCancel={cancelDialog}
            />
          }
        >
          <DialogContent
            siteConditions={props.siteConditions}
            selectedIds={model.dialog.value}
            onToggle={flow(AddSiteConditionsToggled, dispatch)}
          />
        </Dialog>
      )}
    </div>
  );
}

type DialogHeaderProps = {
  onClose: () => void;
};
const DialogHeader = ({ onClose }: DialogHeaderProps): JSX.Element => (
  <div className="flex flex-row justify-between">
    <SectionHeading className="text-xl font-semibold">
      Add Site Conditions
    </SectionHeading>
    <ButtonIcon iconName="close_big" onClick={onClose} />
  </div>
);

type DialogFooterProps = {
  onCancel: () => void;
  onSave: () => void;
};

const DialogFooter = ({ onCancel, onSave }: DialogFooterProps): JSX.Element => (
  <div className="flex flex-row justify-end gap-2">
    <ButtonSecondary label="Cancel" onClick={onCancel} />
    <ButtonPrimary label="Add" onClick={onSave} />
  </div>
);

type DialogContentProps = {
  siteConditions: LibrarySiteCondition[];
  selectedIds: Set<LibrarySiteConditionId>;
  onToggle: (id: LibrarySiteConditionId) => void;
};

const DialogContent = ({
  siteConditions,
  selectedIds,
  onToggle,
}: DialogContentProps): JSX.Element => {
  const selectedSiteConditions = useMemo(
    () =>
      siteConditions
        .filter(sc => isNone(sc.archivedAt))
        .filter(sc => S.elem(eqLibrarySiteConditionId)(sc.id)(selectedIds)),
    [siteConditions, selectedIds]
  );
  const selectedCount = useMemo(
    () => selectedSiteConditions.length,
    [selectedSiteConditions]
  );

  const otherSiteConditions = useMemo(
    () =>
      siteConditions
        .filter(sc => isNone(sc.archivedAt))
        .filter(sc => !S.elem(eqLibrarySiteConditionId)(sc.id)(selectedIds)),
    [siteConditions, selectedIds]
  );
  const otherCount = useMemo(
    () => otherSiteConditions.length,
    [otherSiteConditions]
  );

  return (
    <>
      <div className="flex flex-col gap-2">
        <div className="flex flex-row gap-4 items-center">
          <label className="text-md">Applicable site conditions</label>
          <label className="text-sm font-semibold">{selectedCount}</label>
        </div>
        {selectedSiteConditions.map(sc => (
          <div key={sc.id} className="flex flex-row gap-2">
            <input
              type="checkbox"
              checked={S.elem(eqLibrarySiteConditionId)(sc.id)(selectedIds)}
              onChange={flow(constant(sc.id), onToggle)}
            />
            <label className="text-sm">{sc.name}</label>
          </div>
        ))}

        <div className="flex flex-row gap-4 items-center">
          <label className="text-md">Other site conditions</label>
          <label className="text-sm font-semibold">{otherCount}</label>
        </div>
        {otherSiteConditions.map(sc => (
          <div key={sc.id} className="flex flex-row gap-2">
            <input
              type="checkbox"
              checked={S.elem(eqLibrarySiteConditionId)(sc.id)(selectedIds)}
              onChange={flow(constant(sc.id), onToggle)}
            />
            <label className="text-sm">{sc.name}</label>
          </div>
        ))}
      </div>
    </>
  );
};
