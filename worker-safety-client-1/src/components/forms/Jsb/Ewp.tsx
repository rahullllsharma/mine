import type { Ewp } from "@/api/codecs";
import type { EwpInput } from "@/api/generated/types";
import type { FormField } from "@/utils/formField";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { ValidDateTime } from "@/utils/validation";
import type * as t from "io-ts";
import type * as tt from "io-ts-types";
import type { StepSnapshot } from "../Utils";
import { SectionHeading } from "@urbint/silica";
import { sequenceS } from "fp-ts/lib/Apply";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { constant, flow, pipe } from "fp-ts/lib/function";
import { nonEmptyStringCodec } from "@/utils/validation";
import { initFormField, setDirty, updateFormField } from "@/utils/formField";
import { Input } from "../Basic/Input";
import { FieldGroup } from "../../shared/FieldGroup";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import Labeled from "../Basic/Labeled";
import * as EscEquipmentInformation from "./EscEquipmentInformation";
import * as EwpMetadata from "./EwpMetadata";

export type Model = {
  name: FormField<t.Errors, string, tt.NonEmptyString>;
  metadata: EwpMetadata.Model;
  equipment: EscEquipmentInformation.Model[];
  referencePoints: FormField<t.Errors, string, tt.NonEmptyString>[];
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    name: setDirty(model.name),
    metadata: EwpMetadata.setFormDirty(model.metadata),
    referencePoints: model.referencePoints.map(setDirty),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    name: model.name.raw,
    metadata: EwpMetadata.makeSnapshot(model.metadata),
    equipment: model.equipment.map(EscEquipmentInformation.makeSnapshot),
    referencePoints: model.referencePoints.map(m => m.raw),
  };
}

export function initEmpty(): Model {
  return {
    name: initFormField(nonEmptyStringCodec().decode)(""),
    metadata: EwpMetadata.initEmpty(),
    equipment: [EscEquipmentInformation.initEmpty()],
    referencePoints: [
      initFormField(nonEmptyStringCodec().decode)(""),
      initFormField(nonEmptyStringCodec().decode)(""),
    ],
  };
}

export function init(ewp: Ewp): Model {
  return {
    name: initFormField(nonEmptyStringCodec().decode)(ewp.id),
    metadata: EwpMetadata.init(ewp.metadata),
    equipment: ewp.equipmentInformation.map(EscEquipmentInformation.init),
    referencePoints: ewp.referencePoints.map(
      initFormField(nonEmptyStringCodec().decode)
    ),
  };
}

export const toEwpInput =
  (date: ValidDateTime) =>
  (model: Model): t.Validation<EwpInput> => {
    return sequenceS(E.Apply)({
      id: model.name.val,
      equipmentInformation: pipe(
        model.equipment,
        A.traverse(E.Applicative)(
          EscEquipmentInformation.toEwpEquipmentInformationInput
        )
      ),
      metadata: EwpMetadata.toEwpMetadataInput(date)(model.metadata),
      referencePoints: pipe(
        model.referencePoints,
        A.traverse(E.Applicative)(r => r.val)
      ),
    });
  };

export type Action =
  | {
      type: "NameChanged";
      value: string;
    }
  | {
      type: "MetadataAction";
      action: EwpMetadata.Action;
    }
  | {
      type: "EquipmentAction";
      index: number;
      action: EscEquipmentInformation.Action;
    }
  | {
      type: "ReferencePointChanged";
      index: number;
      value: string;
    }
  | {
      type: "EquipmentAdded";
    }
  | {
      type: "EquipmentRemoved";
      index: number;
    };

export const NameChanged = (value: string): Action => ({
  type: "NameChanged",
  value,
});

export const MetadataAction = (action: EwpMetadata.Action): Action => ({
  type: "MetadataAction",
  action,
});

export const EquipmentAction =
  (index: number) =>
  (action: EscEquipmentInformation.Action): Action => ({
    type: "EquipmentAction",
    index,
    action,
  });

export const ReferencePointChanged =
  (index: number) =>
  (value: string): Action => ({
    type: "ReferencePointChanged",
    index,
    value,
  });

export const EquipmentAdded = (): Action => ({
  type: "EquipmentAdded",
});

export const EquipmentRemoved = (index: number): Action => ({
  type: "EquipmentRemoved",
  index,
});

export function update(model: Model, action: Action): Model {
  switch (action.type) {
    case "NameChanged":
      return {
        ...model,
        name: updateFormField(nonEmptyStringCodec().decode)(action.value),
      };

    case "MetadataAction":
      return {
        ...model,
        metadata: EwpMetadata.update(model.metadata, action.action),
      };
    case "EquipmentAction":
      return {
        ...model,
        equipment: model.equipment.map((m, i) =>
          i === action.index
            ? EscEquipmentInformation.update(m, action.action)
            : m
        ),
      };
    case "ReferencePointChanged":
      return {
        ...model,
        referencePoints: model.referencePoints.map((m, i) =>
          i === action.index
            ? updateFormField(nonEmptyStringCodec().decode)(action.value)
            : m
        ),
      };
    case "EquipmentAdded":
      return {
        ...model,
        equipment: [...model.equipment, EscEquipmentInformation.initEmpty()],
      };

    case "EquipmentRemoved":
      return {
        ...model,
        equipment: pipe(
          model.equipment,
          A.deleteAt(action.index),
          O.getOrElse(() => model.equipment)
        ),
      };
  }
}

export type Props = ChildProps<Model, Action> & {
  isReadOnly?: boolean;
  onRemove: () => void;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  return (
    <>
      <Labeled label="EWP *" className="flex flex-row items-center gap-4">
        <Input
          type="text"
          className="flex-1"
          field={model.name}
          disabled={isReadOnly}
          onChange={flow(NameChanged, dispatch)}
        />
        {!isReadOnly && (
          <ButtonIcon iconName="trash_empty" onClick={props.onRemove} />
        )}
      </Labeled>

      <FieldGroup>
        <EwpMetadata.View
          model={model.metadata}
          dispatch={flow(MetadataAction, dispatch)}
          isReadOnly={isReadOnly}
        />
      </FieldGroup>

      <FieldGroup legend="Reference Points">
        {model.referencePoints.map((m, i) => (
          <Input
            key={i}
            type="text"
            label={`Reference Point ${i + 1} *`}
            field={m}
            disabled={isReadOnly}
            onChange={flow(ReferencePointChanged(i), dispatch)}
          />
        ))}
      </FieldGroup>

      <SectionHeading className="text-xl font-semibold">
        Circuit Breakers
      </SectionHeading>

      {model.equipment.map((m, i) => (
        <FieldGroup key={i}>
          {i === 0 || isReadOnly ? (
            <></>
          ) : (
            <div className="flex flex-row justify-end">
              <ButtonIcon
                iconName="trash_empty"
                onClick={flow(constant(i), EquipmentRemoved, dispatch)}
              />
            </div>
          )}
          <EscEquipmentInformation.View
            model={m}
            dispatch={flow(EquipmentAction(i), dispatch)}
            isReadOnly={isReadOnly}
          />
        </FieldGroup>
      ))}

      {!isReadOnly && (
        <div>
          <ButtonSecondary
            label="Add additional Circuit Breaker"
            iconStart="plus_circle_outline"
            onClick={flow(EquipmentAdded, dispatch)}
          />
        </div>
      )}
    </>
  );
}
