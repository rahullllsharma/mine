import type { Jsb, WorkProcedureId } from "@/api/codecs";
import type { SaveJobSafetyBriefingInput } from "@/api/generated/types";
import type { FormField } from "@/utils/formField";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/lib/Option";
import type * as t from "io-ts";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { StepSnapshot } from "../Utils";
import {
  ActionLabel,
  BodyText,
  CaptionText,
  SectionHeading,
} from "@urbint/silica";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { constNull, constant, flow, identity, pipe } from "fp-ts/lib/function";
import * as tt from "io-ts-types";
import { Lens } from "monocle-ts";
import { useState } from "react";
import Image from "next/image";
import { literalNES } from "@/utils/validation";
import { noEffect } from "@/utils/reducerWithEffect";
import { initFormField, setDirty, updateFormField } from "@/utils/formField";
import MadImage from "public/assets/mad.png";
import FourRulesOfCoverUp from "public/assets/4rulesofcoverup.png";
import Loader from "@/components/shared/loader/Loader";
import { Dialog } from "../Basic/Dialog";
import { MultiSelect } from "../Basic/MultiSelect";
import StepLayout from "../StepLayout";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import Link from "../../shared/link/Link";
import { Checkbox } from "../Basic/Checkbox";
import { Select } from "../Basic/Select";
import { stringLabel } from "../Basic/SelectOption";
import { FieldGroup } from "../../shared/FieldGroup";
import { distributionBulletins } from "./distributionBulletins";

const requiredOptions: (
  i: string[]
) => t.Validation<NonEmptyArray<tt.NonEmptyString>> = tt.nonEmptyArray(
  tt.NonEmptyString
).decode;

const requiredNes = (
  s: Option<tt.NonEmptyString>
): t.Validation<tt.NonEmptyString> =>
  pipe(
    s,
    O.getOrElseW(() => ""),
    tt.withMessage(tt.NonEmptyString, () => "This field is required").decode
  );

const bulletins = distributionBulletins.map(b => ({
  value: b,
  label: b,
  isSelected: false,
}));
const appreachDistances = [
  literalNES("Avoid Contact"),
  literalNES("14 in"),
  literalNES("26 in"),
  literalNES("31 in"),
].map(x => ({ value: x, label: x }));

export type Model = {
  form: {
    distribution_bulletins: {
      selected: boolean;
      field: FormField<t.Errors, string[], NonEmptyArray<tt.NonEmptyString>>;
    };
    four_rules_of_cover_up: {
      selected: boolean;
    };
    mad: {
      selected: boolean;
      field: FormField<t.Errors, Option<tt.NonEmptyString>, tt.NonEmptyString>;
    };
    sdop_switching_procedures: {
      selected: boolean;
    };
    toc: {
      selected: boolean;
    };
    step_touch_potential: {
      selected: boolean;
    };
    otherWorkProcedures: string;
    // deprecated
    section_0: {
      selected: boolean;
    };
    excavation: {
      selected: boolean;
    };
    human_perf_toolkit: {
      selected: boolean;
    };
  };
  madTableDialog: Option<unknown>;
  fourRulesDialog: Option<unknown>;
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    form: {
      ...model.form,
      distribution_bulletins: {
        ...model.form.distribution_bulletins,
        field: setDirty(model.form.distribution_bulletins.field),
      },
      mad: {
        ...model.form.mad,
        field: setDirty(model.form.mad.field),
      },
    },
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    distributionBulletins: {
      selected: model.form.distribution_bulletins.selected,
      values: model.form.distribution_bulletins.field.raw,
    },
    fourRulesOfCoverUp: model.form.four_rules_of_cover_up.selected,
    mad: {
      selected: model.form.mad.selected,
      value: O.getOrElseW(constNull)(model.form.mad.field.raw),
    },
    sdopSwitchingProcedures: model.form.sdop_switching_procedures.selected,
    toc: model.form.toc.selected,
    stepTouchPotential: model.form.step_touch_potential.selected,
  };
}

function lookupWorkProcedure<T extends { id: WorkProcedureId }>(
  wpid: WorkProcedureId
) {
  return (wps: T[]): Option<T> =>
    pipe(
      wps,
      A.findFirst(wp => wp.id === wpid)
    );
}

export function wpLabel(wpid: WorkProcedureId): string {
  switch (wpid) {
    case "distribution_bulletins":
      return "Distribution Bulletins";
    case "four_rules_of_cover_up":
      return "4 Rules of Cover Up";
    case "mad":
      return "MAD";
    case "sdop_switching_procedures":
      return "SDOP Switching Procedures";
    case "toc":
      return "TOC";
    case "step_touch_potential":
      return "Step/Touch Potential";

    // deprecated
    case "excavation":
      return "Excavation";
    case "section_0":
      return "Section 0";
    case "human_perf_toolkit":
      return "Human Perf toolkit";
  }
}

export function toSaveJsbInput(
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> {
  const workProcedureResults = [
    pipe(
      model.form.distribution_bulletins,
      O.fromPredicate(m => m.selected),
      O.map(() =>
        pipe(
          model.form["distribution_bulletins"].field.val,
          E.map(x => ({ id: "distribution_bulletins", values: x }))
        )
      )
    ),
    pipe(
      model.form.four_rules_of_cover_up,
      O.fromPredicate(m => m.selected),
      O.map(() => E.of({ id: "four_rules_of_cover_up", values: [] }))
    ),
    pipe(
      model.form.mad,
      O.fromPredicate(m => m.selected),
      O.map(m =>
        pipe(
          m.field.val,
          E.map(x => ({ id: "mad", values: [x] }))
        )
      )
    ),
    pipe(
      model.form.sdop_switching_procedures,
      O.fromPredicate(m => m.selected),
      O.map(() => E.of({ id: "sdop_switching_procedures", values: [] }))
    ),
    pipe(
      model.form.toc,
      O.fromPredicate(m => m.selected),
      O.map(() => E.of({ id: "toc", values: [] }))
    ),
    pipe(
      model.form.step_touch_potential,
      O.fromPredicate(m => m.selected),
      O.map(() => E.of({ id: "step_touch_potential", values: [] }))
    ),
  ];

  const res = pipe(
    workProcedureResults,
    A.compact,
    A.sequence(E.Applicative),
    E.map(x => ({
      workProcedureSelections: x,
      otherWorkProcedures: model.form.otherWorkProcedures || "",
    }))
  );

  return res;
}

export const init = (jsb: Option<Jsb>): Model => {
  const jsbOtherWorkProcedures = pipe(
    jsb,
    O.map(e => e.otherWorkProcedures)
  );
  const wpsSelected = (id: WorkProcedureId) =>
    pipe(
      jsb,
      O.chain(j => j.workProcedureSelections),
      O.chain(lookupWorkProcedure(id)),
      O.isSome
    );
  const wpsValue = (id: WorkProcedureId) =>
    pipe(
      jsb,
      O.chain(j => j.workProcedureSelections),
      O.chain(lookupWorkProcedure(id)),
      O.fold(
        () => [],
        x => x.values
      )
    );

  return {
    form: {
      distribution_bulletins: {
        field: pipe(
          wpsValue("distribution_bulletins"),
          initFormField(requiredOptions)
        ),
        selected: true,
      },
      four_rules_of_cover_up: {
        selected: wpsSelected("four_rules_of_cover_up"),
      },
      mad: {
        field: pipe(wpsValue("mad"), A.head, initFormField(requiredNes)),
        selected: wpsSelected("mad"),
      },
      sdop_switching_procedures: {
        selected: wpsSelected("sdop_switching_procedures"),
      },
      toc: {
        selected: wpsSelected("toc"),
      },
      step_touch_potential: {
        selected: wpsSelected("step_touch_potential"),
      },

      // deprecated
      section_0: {
        selected: wpsSelected("section_0"),
      },
      excavation: {
        selected: wpsSelected("excavation"),
      },
      human_perf_toolkit: {
        selected: wpsSelected("human_perf_toolkit"),
      },
      otherWorkProcedures: pipe(
        jsbOtherWorkProcedures,
        O.chain(c => c),
        O.fold(
          () => "",
          s => s
        )
      ),
    },
    madTableDialog: O.none,
    fourRulesDialog: O.none,
  };
};

export type Action =
  | {
      type: "WorkProcedureToggled";
      workProcedure: WorkProcedureId;
    }
  | {
      type: "DistributionBulletinAdded";
      value: string;
    }
  | {
      type: "DistributionBulletinRemoved";
      value: string;
    }
  | {
      type: "MadChanged";
      value: Option<tt.NonEmptyString>;
    }
  | {
      type: "MadTableOpened";
    }
  | {
      type: "MadTableClosed";
    }
  | {
      type: "FourRulesOpened";
    }
  | {
      type: "FourRulesClosed";
    }
  | { type: "OtherWorkProceduresChanged"; value: string };

export const WorkProcedureToggled = (
  workProcedure: WorkProcedureId
): Action => ({
  type: "WorkProcedureToggled",
  workProcedure,
});

export const DistributionBulletinAdded = (value: string): Action => ({
  type: "DistributionBulletinAdded",
  value,
});

export const DistributionBulletinRemoved = (value: string): Action => ({
  type: "DistributionBulletinRemoved",
  value,
});

export const MadChanged = (value: Option<tt.NonEmptyString>): Action => ({
  type: "MadChanged",
  value,
});

export const MadTableOpened = (): Action => ({
  type: "MadTableOpened",
});

export const MadTableClosed = (): Action => ({
  type: "MadTableClosed",
});

export const FourRulesOpened = (): Action => ({
  type: "FourRulesOpened",
});

export const FourRulesClosed = (): Action => ({
  type: "FourRulesClosed",
});

export const OtherWorkProceduresChanged = (value: string): Action => ({
  type: "OtherWorkProceduresChanged",
  value,
});

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "WorkProcedureToggled": {
      if (action.workProcedure === "distribution_bulletins") {
        const lens = Lens.fromPath<Model>()(["form", "distribution_bulletins"]);
        return [
          lens.modify(x =>
            x.selected
              ? {
                  field: updateFormField(requiredOptions)([]),
                  selected: !x.selected,
                }
              : { ...x, selected: !x.selected }
          )(model),
          noEffect,
        ];
      } else {
        const lens = Lens.fromPath<Model>()([
          "form",
          action.workProcedure,
          "selected",
        ]);
        return [lens.modify(x => !x)(model), noEffect];
      }
    }
    case "DistributionBulletinAdded": {
      const lens = Lens.fromPath<Model>()([
        "form",
        "distribution_bulletins",
        "field",
      ]);
      return [
        lens.modify(field =>
          updateFormField(requiredOptions)([...field.raw, action.value])
        )(model),
        noEffect,
      ];
    }
    case "DistributionBulletinRemoved": {
      const lens = Lens.fromPath<Model>()([
        "form",
        "distribution_bulletins",
        "field",
      ]);
      return [
        lens.modify(field =>
          updateFormField(requiredOptions)(
            field.raw.filter(x => x !== action.value)
          )
        )(model),
        noEffect,
      ];
    }
    case "MadChanged": {
      const lens = Lens.fromPath<Model>()(["form", "mad", "field"]);
      return [
        lens.modify(_ => updateFormField(requiredNes)(action.value))(model),
        noEffect,
      ];
    }
    case "FourRulesOpened": {
      return [
        {
          ...model,
          fourRulesDialog: O.some({}),
        },
        noEffect,
      ];
    }

    case "FourRulesClosed": {
      return [
        {
          ...model,
          fourRulesDialog: O.none,
        },
        noEffect,
      ];
    }

    case "MadTableOpened": {
      return [
        {
          ...model,
          madTableDialog: O.some({}),
        },
        noEffect,
      ];
    }

    case "MadTableClosed": {
      return [
        {
          ...model,
          madTableDialog: O.none,
        },
        noEffect,
      ];
    }
    case "OtherWorkProceduresChanged": {
      return [
        {
          ...model,
          form: {
            ...model.form,
            otherWorkProcedures: action.value,
          },
        },
        noEffect,
      ];
    }
  }
};

export const wpValue = (wpid: WorkProcedureId, model: Model): Array<string> => {
  switch (wpid) {
    case "distribution_bulletins":
      return model.form.distribution_bulletins.field.raw;

    case "mad":
      return [O.getOrElse(() => "")(model.form.mad.field.raw)];

    case "section_0":
    case "four_rules_of_cover_up":
    case "sdop_switching_procedures":
    case "toc":
    case "excavation":
    case "step_touch_potential":
    case "human_perf_toolkit":
      return [];
  }
};

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const showError = (field: FormField<t.Errors, unknown, unknown>) =>
    field.dirty && E.isLeft(field.val);

  const bulletin = model.form.distribution_bulletins;
  const mads = model.form.mad;
  const MAD_LABEL = "MAD";
  const [loading, setLoading] = useState(true);
  return (
    <>
      <StepLayout>
        <div className="flex flex-col px-4 md:px-0 gap-6">
          <div className="flex flex-col md:flex-row justify-between">
            <SectionHeading className="text-xl font-semibold">
              Work Procedures
            </SectionHeading>
          </div>
          <div className="flex flex-wrap justify-between items-center pd-4 mb-[-1rem] w-full md:flex-col md:items-start lg:flex-row lg:items-center">
            <CaptionText className="text-brand-gray-70 font-semibold">
              Distribution Bulletins *
            </CaptionText>
            <Link
              label="Distribution Bulletins"
              iconRight="external_link"
              href="https://mobi.southernco.com/D_Bulletins/home"
              target="_blank"
              className="gap-2 flex items-center w-full md:w-auto"
            />
          </div>
          <MultiSelect
            options={bulletins}
            selected={model.form.distribution_bulletins.field.raw}
            onSelected={flow(DistributionBulletinAdded, dispatch)}
            onRemoved={flow(DistributionBulletinRemoved, dispatch)}
            disabled={isReadOnly}
            renderLabel={identity}
            optionKey={identity}
            className="ml-15"
            typeahead
            hasError={bulletin.field.dirty && E.isLeft(bulletin.field.val)}
            placeholder="Please select distribution bulletins"
          />
          {model.form.distribution_bulletins.selected &&
            showError(bulletin.field) &&
            bulletin.field.raw.length === 0 && (
              <BodyText className="text-red-500 text-sm mt-[-1rem]">
                Please select at least one distribution bulletin
              </BodyText>
            )}
          <div className="flex flex-row justify-between items-start gap-1 flex-wrap md:flex-col md:items-start lg:flex-row">
            <WorkProcedureSelection
              name={wpLabel("four_rules_of_cover_up")}
              selected={model.form.four_rules_of_cover_up.selected}
              disabled={isReadOnly}
              onToggled={flow(
                constant<WorkProcedureId>("four_rules_of_cover_up"),
                WorkProcedureToggled,
                dispatch
              )}
            >
              <Link
                label="Additional documentation"
                iconRight="external_link"
                href="https://soco365.sharepoint.com/:b:/r/sites/GPCSafetyandHealthALL/Shared Documents/General/eJSB/4 RULES OF COVER UP.pdf?csf=1&web=1&e=XZR0v1"
                target="_blank"
                className="gap-2 flex items-center w-full md:w-auto"
              />
            </WorkProcedureSelection>
            <div className="flex justify-between gap-1 flex-wrap">
              <Link
                label="4 Rules of Cover-Up"
                iconRight="external_link"
                className="gap-2 flex md:w-auto items-baseline"
                onClick={flow(FourRulesOpened, dispatch)}
              />
            </div>
          </div>

          <div className="flex flex-row justify-between items-center gap-1 flex-wrap md:flex-col md:items-start lg:flex-row lg:items-center">
            <WorkProcedureSelection
              name={MAD_LABEL}
              selected={model.form.mad.selected}
              disabled={isReadOnly}
              onToggled={flow(
                constant<WorkProcedureId>("mad"),
                WorkProcedureToggled,
                dispatch
              )}
            />
            <Link
              label="Minimum Approach Distance"
              iconRight="external_link"
              className="gap-2 flex items-center w-full md:w-auto"
              onClick={flow(MadTableOpened, dispatch)}
            />
          </div>
          {model.form.mad.selected && (
            <Select
              label="Minimum Approach Distance *"
              options={appreachDistances}
              renderLabel={stringLabel}
              optionKey={identity}
              selected={model.form.mad.field.raw}
              disabled={isReadOnly}
              onSelected={flow(MadChanged, dispatch)}
              hasError={mads.field.dirty && E.isLeft(mads.field.val)}
              className="mr-2"
            />
          )}
          {model.form.mad.selected && showError(mads.field) && (
            <BodyText className="text-red-500 text-sm ml-5">
              {E.isLeft(mads.field.val) &&
                mads.field.val.left.map(error => error.message)}
            </BodyText>
          )}
          <div className="flex flex-row justify-between items-center gap-1 flex-wrap md:flex-col md:items-start lg:flex-row lg:items-center">
            <WorkProcedureSelection
              name={wpLabel("sdop_switching_procedures")}
              selected={model.form.sdop_switching_procedures.selected}
              disabled={isReadOnly}
              onToggled={flow(
                constant<WorkProcedureId>("sdop_switching_procedures"),
                WorkProcedureToggled,
                dispatch
              )}
            />
            <Link
              label="Switching Procedures"
              iconRight="external_link"
              href="https://soco365.sharepoint.com/sites/intra_GPC_Power_Delivery/_layouts/15/viewer.aspx?sourcedoc={fed21851-6fba-4102-b4b0-69f64e987f8d}"
              target="_blank"
              className="gap-2 flex items-center w-full md:w-auto"
            />
          </div>
          <div className="flex flex-row justify-between items-center gap-1 flex-wrap md:flex-col md:items-start lg:flex-row lg:items-center">
            <WorkProcedureSelection
              name={wpLabel("toc")}
              selected={model.form.toc.selected}
              disabled={isReadOnly}
              onToggled={flow(
                constant<WorkProcedureId>("toc"),
                WorkProcedureToggled,
                dispatch
              )}
            />
            <Link
              label="TOC Request Form"
              iconRight="external_link"
              href="https://mobi.southernco.com/DCC_TOC_REQUEST/TOC"
              target="_blank"
              className="gap-2 flex items-center w-full md:w-auto"
            />
          </div>
          <WorkProcedureSelection
            name={wpLabel("step_touch_potential")}
            selected={model.form.step_touch_potential.selected}
            disabled={isReadOnly}
            onToggled={flow(
              constant<WorkProcedureId>("step_touch_potential"),
              WorkProcedureToggled,
              dispatch
            )}
          ></WorkProcedureSelection>
        </div>
        <div className=" items-center  gap-1 flex-wrap">
          <Link
            label="Best Work Practices"
            iconRight="external_link"
            href="https://soco365.sharepoint.com/sites/intra_GPC_Safety_and_Health/SitePages/Best-Work-Practices.aspx"
            target="_blank"
            className="gap-2 flex items-center w-full md:w-auto"
          />
        </div>
        <FieldGroup className="bg-transparent !p-0">
          <CaptionText className="block md:text-sm text-neutral-shade-75 font-semibold leading-normal">
            If applicable, specify other work procedures or special precautions
          </CaptionText>
          <textarea
            className="w-full h-24 p-2 border-solid border-[1px] border-brand-gray-40 rounded"
            value={model.form.otherWorkProcedures}
            disabled={isReadOnly}
            onChange={e =>
              pipe(e.target.value, OtherWorkProceduresChanged, dispatch)
            }
          />
        </FieldGroup>
      </StepLayout>

      {O.isSome(model.madTableDialog) && (
        <Dialog
          header={
            <div className="flex flex-row justify-between">
              <SectionHeading className="text-xl font-semibold">
                Minimum Approach Distance
              </SectionHeading>
              <ButtonIcon
                iconName="close_big"
                onClick={flow(MadTableClosed, dispatch)}
              />
            </div>
          }
        >
          <div className="relative">
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <Loader iconOnly />
              </div>
            )}
            <Image
              src={MadImage}
              alt="Minimum Approach Distance"
              objectFit="contain"
              onLoadingComplete={() => setLoading(false)}
            />
          </div>
        </Dialog>
      )}
      {O.isSome(model.fourRulesDialog) && (
        <Dialog
          size="flex"
          header={
            <div className="flex flex-row justify-between">
              <SectionHeading className="text-xl font-semibold">
                4 Rules of cover up
              </SectionHeading>
              <ButtonIcon
                iconName="close_big"
                onClick={flow(FourRulesClosed, dispatch)}
              />
            </div>
          }
        >
          <Image
            src={FourRulesOfCoverUp}
            alt="4 Rules of cover up"
            width={630}
            height={300}
          />
        </Dialog>
      )}
    </>
  );
}

type WorkProcedureSelectionProps = {
  name: string;
  selected: boolean;
  disabled?: boolean;
  onToggled: () => void;
  children?: React.ReactNode;
  required?: boolean;
};

function WorkProcedureSelection({
  name,
  selected,
  onToggled,
  children,
  disabled,
  required,
}: WorkProcedureSelectionProps): JSX.Element {
  return (
    <div className="flex flex-col">
      <div className="flex flex-row">
        <Checkbox checked={selected} onClick={onToggled} disabled={disabled} />
        <ActionLabel>
          {name}
          {required && <span className="text-red-500">*</span>}
        </ActionLabel>
      </div>
      {selected && children && <div className="mt-4">{children}</div>}
    </div>
  );
}
