import type { EwpMetadata } from "@/api/codecs";
import type { EwpMetadataInput } from "@/api/generated/types";
import type { FormField } from "@/utils/formField";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { ValidDateTime, ValidDuration } from "@/utils/validation";
import type * as t from "io-ts";
import type * as tt from "io-ts-types";
import type { StepSnapshot } from "../Utils";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { flow, pipe } from "fp-ts/lib/function";
import { nonEmptyStringCodec, validDurationCodecS } from "@/utils/validation";
import { initFormField, setDirty, updateFormField } from "@/utils/formField";
import { Input } from "../Basic/Input";

// Function to format date type to null value initially
const decodeTimeCompleted = (
  raw: string
): t.Validation<O.Option<ValidDuration>> =>
  raw === ""
    ? E.right(O.none)
    : pipe(validDurationCodecS.decode(raw), E.map(O.some));

export type Model = {
  timeIssued: FormField<t.Errors, string, ValidDuration>;
  timeCompleted: FormField<t.Errors, string, O.Option<ValidDuration>>;
  procedure: FormField<t.Errors, string, tt.NonEmptyString>;
  issuedBy: FormField<t.Errors, string, tt.NonEmptyString>;
  receivedBy: FormField<t.Errors, string, tt.NonEmptyString>;
  isRemote: boolean;
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    timeIssued: setDirty(model.timeIssued),
    timeCompleted: setDirty(model.timeCompleted),
    procedure: setDirty(model.procedure),
    issuedBy: setDirty(model.issuedBy),
    receivedBy: setDirty(model.receivedBy),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    timeIssued: model.timeIssued.raw,
    timeCompleted: model.timeCompleted.raw,
    procedure: model.procedure.raw,
    issuedBy: model.issuedBy.raw,
    receivedBy: model.receivedBy.raw,
    remote: model.isRemote,
  };
}

export function initEmpty(): Model {
  return {
    timeIssued: initFormField(validDurationCodecS.decode)(""),
    timeCompleted: initFormField(decodeTimeCompleted)(""),
    procedure: initFormField(nonEmptyStringCodec().decode)(""),
    issuedBy: initFormField(nonEmptyStringCodec().decode)(""),
    receivedBy: initFormField(nonEmptyStringCodec().decode)(""),
    isRemote: false,
  };
}

export function init(ewp: EwpMetadata): Model {
  return {
    timeIssued: pipe(
      ewp.issued.toFormat("HH:mm"),
      initFormField(validDurationCodecS.decode)
    ),
    timeCompleted: pipe(
      ewp.completed,
      O.fold(
        () => "", // ewp.completed is None, return an empty string
        completed => completed.toFormat("HH:mm") // ewp.completed is Some, convert it to a formatted date
      ),
      value => initFormField(decodeTimeCompleted)(value)
    ),
    procedure: pipe(ewp.procedure, initFormField(nonEmptyStringCodec().decode)),
    issuedBy: pipe(ewp.issuedBy, initFormField(nonEmptyStringCodec().decode)),
    receivedBy: pipe(
      ewp.receivedBy,
      initFormField(nonEmptyStringCodec().decode)
    ),
    isRemote: ewp.remote,
  };
}

export const toEwpMetadataInput =
  (date: ValidDateTime) =>
  (model: Model): t.Validation<EwpMetadataInput> => {
    const formatDateTime = (time: ValidDuration) =>
      date.startOf("day").plus(time).toISO() || "";
    const formatCompleted = (completed: O.Option<ValidDuration>) =>
      pipe(
        completed,
        O.map(formatDateTime),
        O.toNullable // Return an Null if completed is None
      );

    return sequenceS(E.Apply)({
      completed: pipe(model.timeCompleted.val, E.map(formatCompleted)),
      issued: pipe(model.timeIssued.val, E.map(formatDateTime)),
      procedure: model.procedure.val,
      issuedBy: model.issuedBy.val,
      receivedBy: model.receivedBy.val,
      remote: E.right(model.isRemote),
    });
  };

export type Action =
  | {
      type: "TimeIssuedChanged";
      value: string;
    }
  | {
      type: "TimeCompletedChanged";
      value: string;
    }
  | {
      type: "ProcedureChanged";
      value: string;
    }
  | {
      type: "IssuedByChanged";
      value: string;
    }
  | {
      type: "ReceivedByChanged";
      value: string;
    };

export const TimeIssuedChanged = (value: string): Action => ({
  type: "TimeIssuedChanged",
  value,
});

export const TimeCompletedChanged = (value: string): Action => ({
  type: "TimeCompletedChanged",
  value,
});

export const ProcedureChanged = (value: string): Action => ({
  type: "ProcedureChanged",
  value,
});

export const IssuedByChanged = (value: string): Action => ({
  type: "IssuedByChanged",
  value,
});

export const ReceivedByChanged = (value: string): Action => ({
  type: "ReceivedByChanged",
  value,
});

export function update(model: Model, action: Action): Model {
  switch (action.type) {
    case "TimeIssuedChanged":
      return {
        ...model,
        timeIssued: updateFormField(validDurationCodecS.decode)(action.value),
      };
    case "TimeCompletedChanged":
      return {
        ...model,
        timeCompleted: updateFormField(decodeTimeCompleted)(action.value),
      };
    case "ProcedureChanged":
      return {
        ...model,
        procedure: pipe(
          action.value,
          updateFormField(nonEmptyStringCodec().decode)
        ),
      };
    case "IssuedByChanged":
      return {
        ...model,
        issuedBy: updateFormField(nonEmptyStringCodec().decode)(action.value),
      };
    case "ReceivedByChanged":
      return {
        ...model,
        receivedBy: updateFormField(nonEmptyStringCodec().decode)(action.value),
      };
  }
}

export type Props = ChildProps<Model, Action> & {
  isReadOnly?: boolean;
};
export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  return (
    <>
      <Input
        type="time"
        label="Time Issued *"
        field={model.timeIssued}
        disabled={isReadOnly}
        onChange={flow(TimeIssuedChanged, dispatch)}
      />
      <Input
        type="time"
        label="Time Completed"
        field={model.timeCompleted}
        disabled={isReadOnly}
        onChange={flow(TimeCompletedChanged, dispatch)}
      />
      <Input
        type="text"
        label="Procedure *"
        field={model.procedure}
        disabled={isReadOnly}
        onChange={flow(ProcedureChanged, dispatch)}
      />
      <Input
        type="text"
        label="Issued By *"
        field={model.issuedBy}
        disabled={isReadOnly}
        onChange={flow(IssuedByChanged, dispatch)}
      />
      <Input
        type="text"
        label="Received By *"
        field={model.receivedBy}
        disabled={isReadOnly}
        onChange={flow(ReceivedByChanged, dispatch)}
      />
    </>
  );
}
