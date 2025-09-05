import type { FormField } from "@/utils/formField";
import type { Option } from "fp-ts/lib/Option";

import type { Jsb } from "@/api/codecs";
import type {
  SaveJobSafetyBriefingInput,
  Voltage,
} from "@/api/generated/types";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { ValidDateTime } from "@/utils/validation";
import type { StepSnapshot } from "../Utils";
import type * as t from "io-ts";
import { SectionHeading } from "@urbint/silica";
import { sequenceS } from "fp-ts/lib/Apply";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { constNull, constant, flow, identity, pipe } from "fp-ts/lib/function";
import { intCodecS } from "@/utils/validation";
import { initFormField, setDirty, updateFormField } from "@/utils/formField";
import { VoltageType } from "@/api/generated/types";
import { InputRaw } from "../Basic/Input";
import { MultiSelect } from "../Basic/MultiSelect";
import { Select } from "../Basic/Select";
import StepLayout from "../StepLayout";
import { FieldGroup } from "../../shared/FieldGroup";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import Link from "../../shared/link/Link";
import { stringLabel } from "../Basic/SelectOption";
import * as Ewp from "./Ewp";

const arcFlashCategories = [
  { value: "1", label: "Category 1" },
  { value: "2", label: "Category 2" },
  { value: "3", label: "Category 3" },
  { value: "4", label: "Category 4" },
];

const primaryVoltages = [
  { value: "2.4", label: "2.4kV" },
  { value: "4", label: "4kV" },
  { value: "7.2", label: "7.2kV" },
  { value: "11.4", label: "11.4kV" },
  { value: "12", label: "12kV" },
  { value: "14.4", label: "14.4kV" },
  { value: "20", label: "20kV" },
  { value: "25", label: "25kV" },
  { value: "Other", label: "Other" },
];

const secondaryVoltages = [
  { value: "120", label: "120v" },
  { value: "208", label: "208v" },
  { value: "240", label: "240v" },
  { value: "277", label: "277v" },
  { value: "480", label: "480v" },
];

const transmissionVoltages = [
  { value: "46", label: "46kV" },
  { value: "69", label: "69kV" },
  { value: "115", label: "115kV" },
  { value: "161", label: "161kV" },
  { value: "230", label: "230kV" },
  { value: "500", label: "500kV" },
];

export const voltageOptions = {
  [VoltageType.Primary]: primaryVoltages,
  [VoltageType.Secondary]: secondaryVoltages,
  [VoltageType.Transmission]: transmissionVoltages,
};

export const lookupVoltageLabel =
  (voltages: { value: string; label: string }[]) =>
  (val: number): Option<string> =>
    pipe(
      voltages,
      A.findFirst(v => v.value === val.toString()),
      O.map(v => v.label)
    );

const optionIntFromOptionString = (
  v: Option<string>
): t.Validation<Option<t.Int>> =>
  O.isSome(v)
    ? pipe(
        intCodecS.decode(v.value),
        E.map(x => O.some(x))
      )
    : E.right(O.none);

export type Model = {
  arcFlashCategory: FormField<t.Errors, Option<string>, Option<t.Int>>;
  primaryVoltage: FormField<t.Errors, string[], string[]>;
  otherPrimaryVoltage: string[];
  secondaryVoltage: FormField<t.Errors, string[], string[]>;
  transmissionVoltage: FormField<t.Errors, Option<string>, Option<string>>;
  clearancePoints: string;
  ewps: Ewp.Model[];
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    arcFlashCategory: setDirty(model.arcFlashCategory),
    primaryVoltage: setDirty(model.primaryVoltage),
    secondaryVoltage: setDirty(model.secondaryVoltage),
    transmissionVoltage: setDirty(model.transmissionVoltage),
    ewps: model.ewps.map(Ewp.setFormDirty),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    arcFlashCategory: O.getOrElseW(constNull)(model.arcFlashCategory.raw),
    primaryVoltage: model.primaryVoltage.raw,
    secondaryVoltage: model.secondaryVoltage.raw,
    transmissionVoltage: O.getOrElseW(constNull)(model.transmissionVoltage.raw),
    clearancePoints: model.clearancePoints,
    ewps: model.ewps.map(Ewp.makeSnapshot),
  };
}

export function init(jsb: Option<Jsb>): Model {
  const escData = pipe(
    jsb,
    O.chain(j => j.energySourceControl)
  );

  const findVoltages = (
    voltageType:
      | VoltageType.Primary
      | VoltageType.Secondary
      | VoltageType.Transmission
  ) =>
    pipe(
      escData,
      O.fold(
        () => [],
        esc =>
          pipe(
            esc.voltages,
            A.filter(v => v.type === voltageType),
            A.filterMap(v =>
              pipe(
                voltageOptions[voltageType],
                A.findFirst(({ value }) => v.valueStr.toString() === value)
              )
            ),
            A.map(({ value }) => value)
          )
      )
    );

  const savedPrimaryVoltage = pipe(
    escData,
    O.chain(val =>
      pipe(
        val.voltages,
        A.filter(voltage => voltage.type === VoltageType.Primary),
        A.map(voltage => voltage.valueStr), // Extract only the values
        values => (values.length > 0 ? O.some(values) : O.none) // Wrap in Option
      )
    )
  );

  const excludedPrimaryVoltages = primaryVoltages.map(({ value }) => value);
  const otherPrimaryVoltages = pipe(
    savedPrimaryVoltage,
    O.fold(
      () => [], // Handle the case when savedPrimaryVoltage is None
      (voltages: string[]) =>
        voltages.filter(voltage => !excludedPrimaryVoltages.includes(voltage))
    )
  );
  return {
    arcFlashCategory: pipe(
      escData,
      O.chain(esc => esc.arcFlashCategory),
      O.map(afc => afc.toString()),
      initFormField(optionIntFromOptionString)
    ),
    primaryVoltage: pipe(
      findVoltages(VoltageType.Primary),
      initFormField<t.Errors, string[], string[]>(E.right)
    ),
    otherPrimaryVoltage: otherPrimaryVoltages,
    secondaryVoltage: pipe(
      findVoltages(VoltageType.Secondary),
      initFormField<t.Errors, string[], string[]>(E.right)
    ),
    transmissionVoltage: pipe(
      findVoltages(VoltageType.Transmission),
      A.head,
      initFormField<t.Errors, Option<string>, Option<string>>(E.right)
    ),
    clearancePoints: pipe(
      escData,
      O.chain(esc => esc.clearancePoints),
      O.getOrElse(() => "")
    ),
    ewps: pipe(
      escData,
      O.fold(
        () => [],
        esc => pipe(esc.ewp, A.map(Ewp.init))
      )
    ),
  };
}

export const toSaveJsbInput = (
  date: ValidDateTime,
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> => {
  const primaryVoltageResult = pipe(
    model.primaryVoltage.val,
    E.map(
      A.map(v => ({
        type: VoltageType.Primary,
        unit: "kV",
        valueStr: v,
      }))
    )
  );

  const secondaryVoltageResult = pipe(
    model.secondaryVoltage.val,
    E.map(
      A.map(v => ({
        type: VoltageType.Secondary,
        unit: "v",
        valueStr: v,
      }))
    )
  );

  const transmissionVoltageResult = pipe(
    model.transmissionVoltage.val,
    E.map(
      O.map(v => ({
        type: VoltageType.Transmission,
        unit: "kV",
        valueStr: v,
      }))
    )
  );

  const otherPrimaryVoltageResult = model.otherPrimaryVoltage.map(v => ({
    type: VoltageType.Primary,
    unit: "kV",
    valueStr: v,
  }));

  const primaryAndOtherVoltagesResult = pipe(
    primaryVoltageResult,
    E.chain(initialPrimaryVoltages => {
      if (model.primaryVoltage.raw.includes("Other")) {
        // Combine primary voltages with other primary voltages
        const allPrimaryVoltages = [
          ...initialPrimaryVoltages,
          ...otherPrimaryVoltageResult,
        ];
        // Wrap the combined voltages in an Either
        return E.right(allPrimaryVoltages);
      } else {
        return E.right(initialPrimaryVoltages); // "Other" already included in primary voltages
      }
    })
  );
  const combineVoltages =
    (primary: Voltage[]) =>
    (secondary: Voltage[]) =>
    (transmission: Option<Voltage>): Voltage[] =>
      pipe(A.compact([transmission]), A.concat(secondary), A.concat(primary));

  const res = pipe(
    sequenceS(E.Apply)({
      arcFlashCategory: pipe(
        model.arcFlashCategory.val,
        E.map(O.getOrElseW(() => null))
      ),
      clearancePoints: E.right(model.clearancePoints),
      voltages: pipe(
        E.of(combineVoltages),
        E.ap(primaryAndOtherVoltagesResult),
        E.ap(secondaryVoltageResult),
        E.ap(transmissionVoltageResult)
      ),
      ewp: pipe(model.ewps, A.traverse(E.Applicative)(Ewp.toEwpInput(date))),
      transferOfControl: E.right(false),
    }),
    E.map(r => ({
      energySourceControl: r,
    }))
  );

  return res;
};

export type Action =
  | {
      type: "ArcFlashCategoryChanged";
      value: Option<string>;
    }
  | {
      type: "ClearancePointsChanged";
      value: string;
    }
  | {
      type: "OtherPrimaryVoltage";
      value: string;
    }
  | {
      type: "PrimaryVoltageAdded";
      value: string;
    }
  | {
      type: "PrimaryVoltageRemoved";
      value: string;
    }
  | {
      type: "SecondaryVoltageAdded";
      value: string;
    }
  | {
      type: "SecondaryVoltageRemoved";
      value: string;
    }
  | {
      type: "TransmissionVoltageChanged";
      value: Option<string>;
    }
  | {
      type: "EwpAdded";
    }
  | {
      type: "EwpRemoved";
      index: number;
    }
  | {
      type: "EwpAction";
      index: number;
      action: Ewp.Action;
    };

export const ArcFlashCategoryChanged = (value: Option<string>): Action => ({
  type: "ArcFlashCategoryChanged",
  value,
});

export const ClearancePointsChanged = (value: string): Action => ({
  type: "ClearancePointsChanged",
  value,
});

export const OtherPrimaryVoltage = (value: string): Action => ({
  type: "OtherPrimaryVoltage",
  value,
});

export const PrimaryVoltageAdded = (value: string): Action => ({
  type: "PrimaryVoltageAdded",
  value,
});

export const PrimaryVoltageRemoved = (value: string): Action => ({
  type: "PrimaryVoltageRemoved",
  value,
});

export const SecondaryVoltageAdded = (value: string): Action => ({
  type: "SecondaryVoltageAdded",
  value,
});

export const SecondaryVoltageRemoved = (value: string): Action => ({
  type: "SecondaryVoltageRemoved",
  value,
});

export const TransmissionVoltageChanged = (value: Option<string>): Action => ({
  type: "TransmissionVoltageChanged",
  value,
});

export const EwpAdded = (): Action => ({
  type: "EwpAdded",
});

export const EwpRemoved = (index: number): Action => ({
  type: "EwpRemoved",
  index,
});

export const EwpAction =
  (index: number) =>
  (action: Ewp.Action): Action => ({
    type: "EwpAction",
    index,
    action,
  });

export function update(model: Model, action: Action): Model {
  switch (action.type) {
    case "ArcFlashCategoryChanged":
      return {
        ...model,
        arcFlashCategory: updateFormField(optionIntFromOptionString)(
          action.value
        ),
      };
    case "ClearancePointsChanged":
      return {
        ...model,
        clearancePoints: action.value,
      };
    case "OtherPrimaryVoltage":
      const voltageArray = action.value.toString().split(",");

      return {
        ...model,
        otherPrimaryVoltage: model.primaryVoltage.raw.includes("Other")
          ? voltageArray
          : [],
      };
    case "PrimaryVoltageAdded":
      return {
        ...model,
        primaryVoltage: updateFormField<t.Errors, string[], string[]>(E.right)([
          ...model.primaryVoltage.raw,
          action.value,
        ]),
      };
    case "PrimaryVoltageRemoved":
      return {
        ...model,
        primaryVoltage: updateFormField<t.Errors, string[], string[]>(E.right)(
          model.primaryVoltage.raw.filter(v => v !== action.value)
        ),
      };
    case "SecondaryVoltageAdded":
      return {
        ...model,
        secondaryVoltage: updateFormField<t.Errors, string[], string[]>(
          E.right
        )([...model.secondaryVoltage.raw, action.value]),
      };
    case "SecondaryVoltageRemoved":
      return {
        ...model,
        secondaryVoltage: updateFormField<t.Errors, string[], string[]>(
          E.right
        )(model.secondaryVoltage.raw.filter(v => v !== action.value)),
      };
    case "TransmissionVoltageChanged":
      return {
        ...model,
        transmissionVoltage: updateFormField<
          t.Errors,
          Option<string>,
          Option<string>
        >(E.right)(action.value),
      };
    case "EwpAdded":
      return {
        ...model,
        ewps: [...model.ewps, Ewp.initEmpty()],
      };

    case "EwpRemoved":
      return {
        ...model,
        ewps: model.ewps.filter((_, i) => i !== action.index),
      };

    case "EwpAction":
      return {
        ...model,
        ewps: pipe(
          model.ewps,
          A.mapWithIndex((i, ewp) =>
            i === action.index ? Ewp.update(ewp, action.action) : ewp
          )
        ),
      };
  }
}

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
};
export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;
  const isOtherSelected = model.primaryVoltage.raw.includes("Other");

  return (
    <StepLayout>
      <FieldGroup>
        <Select
          label="Arc Flash Category"
          options={arcFlashCategories}
          selected={model.arcFlashCategory.raw}
          disabled={isReadOnly}
          onSelected={flow(ArcFlashCategoryChanged, dispatch)}
          renderLabel={stringLabel}
          optionKey={k => k.toString()}
        />

        <MultiSelect
          label="Primary Voltage"
          options={voltageOptions[VoltageType.Primary]}
          selected={model.primaryVoltage.raw}
          disabled={isReadOnly}
          onSelected={flow(PrimaryVoltageAdded, dispatch)}
          onRemoved={flow(PrimaryVoltageRemoved, dispatch)}
          renderLabel={identity}
          optionKey={k => k.toString()}
        />

        {isOtherSelected && (
          <InputRaw
            label="Voltage (in kV)"
            value={model.otherPrimaryVoltage.toString()}
            disabled={isReadOnly}
            onChange={flow(OtherPrimaryVoltage, dispatch)}
            regex={/[^0-9.,]/g}
          />
        )}

        <MultiSelect
          label="Secondary Voltage"
          options={voltageOptions[VoltageType.Secondary]}
          selected={model.secondaryVoltage.raw}
          disabled={isReadOnly}
          onSelected={flow(SecondaryVoltageAdded, dispatch)}
          onRemoved={flow(SecondaryVoltageRemoved, dispatch)}
          renderLabel={identity}
          optionKey={k => k.toString()}
        />

        <Select
          label="Transmission Voltage"
          options={voltageOptions[VoltageType.Transmission]}
          selected={model.transmissionVoltage.raw}
          disabled={isReadOnly}
          onSelected={flow(TransmissionVoltageChanged, dispatch)}
          renderLabel={stringLabel}
          optionKey={k => k.toString()}
        />

        <InputRaw
          label="Clearance Points"
          value={model.clearancePoints}
          disabled={isReadOnly}
          onChange={flow(ClearancePointsChanged, dispatch)}
        />
      </FieldGroup>
      <div className=" px-4 md:px-0">
        <Link
          iconLeft="external_link"
          label="Georgia 811"
          href="https://geocall.ga811.com/geocall/portal"
          target="_blank"
        />
        <div className="flex flex-row justify-between">
          <SectionHeading className="text-xl font-semibold">EWP</SectionHeading>
          {!isReadOnly && (
            <ButtonSecondary
              onClick={flow(EwpAdded, dispatch)}
              label="Add additional EWP"
              iconStart="plus_circle_outline"
            />
          )}
        </div>
        <Link
          iconLeft="external_link"
          label="EWP request form"
          href="https://mobi.southernco.com/GPC-DCC/EWP"
          target="_blank"
        />

        {model.ewps.map((ewp, i) => (
          <Ewp.View
            key={i}
            model={ewp}
            dispatch={flow(EwpAction(i), dispatch)}
            onRemove={flow(constant(i), EwpRemoved, dispatch)}
            isReadOnly={isReadOnly}
          />
        ))}
      </div>
    </StepLayout>
  );
}
