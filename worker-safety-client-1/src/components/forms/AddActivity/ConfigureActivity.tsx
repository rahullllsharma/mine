import type { FormField } from "@/utils/formField";
import type { ValidDateTime } from "@/utils/validation";
import type * as t from "io-ts";
import type * as tt from "io-ts-types";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { Either } from "fp-ts/lib/Either";
import { flow, identity, pipe } from "fp-ts/lib/function";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import {
  nonEmptyStringCodec,
  showValidationError,
  validDateTimeCodecS,
} from "@/utils/validation";
import { fieldDef, setDirty } from "@/utils/formField";
import { ActivityStatus } from "@/api/generated/types";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { Input } from "../Basic/Input";
import { Select } from "../Basic/Select";
import { stringLabel } from "../Basic/SelectOption";

const activityStatusOptions = [
  { value: ActivityStatus.NotStarted, label: "Not Started" },
  { value: ActivityStatus.InProgress, label: "In Progress" },
  { value: ActivityStatus.Complete, label: "Completed" },
  { value: ActivityStatus.NotCompleted, label: "Not Completed" },
];

export const formDefinition = {
  name: fieldDef(nonEmptyStringCodec().decode),
  startDate: fieldDef(validDateTimeCodecS.decode),
  endDate: fieldDef(validDateTimeCodecS.decode),
};

export type Model = {
  name: FormField<t.Errors, string, tt.NonEmptyString>;
  startDate: FormField<t.Errors, string, ValidDateTime>;
  endDate: FormField<t.Errors, string, ValidDateTime>;
  status: ActivityStatus;
};

type InitData = {
  name?: string;
  startDate?: string;
  endDate?: string;
  status?: ActivityStatus;
};

export const init = ({
  name,
  startDate,
  endDate,
  status,
}: InitData = {}): Model => ({
  name: formDefinition.name.init(name || ""),
  startDate: formDefinition.startDate.init(startDate || ""),
  endDate: formDefinition.endDate.init(endDate || ""),
  status: status || ActivityStatus.NotStarted,
});

export const withDirtyForm = (model: Model): Model => ({
  ...model,
  name: setDirty(model.name),
  startDate: setDirty(model.startDate),
  endDate: setDirty(model.endDate),
});

export type Result = {
  name: tt.NonEmptyString;
  startDate: ValidDateTime;
  endDate: ValidDateTime;
  status: ActivityStatus;
};

export const result = (model: Model): Either<string, Result> =>
  pipe(
    sequenceS(E.Apply)({
      name: model.name.val,
      startDate: model.startDate.val,
      endDate: model.endDate.val,
      status: E.right(model.status),
    }),
    E.mapLeft(showValidationError)
  );

export type Action =
  | {
      type: "NameChanged";
      value: string;
    }
  | {
      type: "StartDateChanged";
      value: string;
    }
  | {
      type: "EndDateChanged";
      value: string;
    }
  | {
      type: "StatusChanged";
      value: ActivityStatus;
    };

export const NameChanged = (value: string): Action => ({
  type: "NameChanged",
  value,
});

export const StartDateChanged = (value: string): Action => ({
  type: "StartDateChanged",
  value,
});

export const EndDateChanged = (value: string): Action => ({
  type: "EndDateChanged",
  value,
});

export const StatusChanged = (value: ActivityStatus): Action => ({
  type: "StatusChanged",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "NameChanged":
      return {
        ...model,
        name: formDefinition.name.update(action.value),
      };

    case "StartDateChanged":
      return {
        ...model,
        startDate: formDefinition.startDate.update(action.value),
      };

    case "EndDateChanged":
      return {
        ...model,
        endDate: formDefinition.endDate.update(action.value),
      };

    case "StatusChanged":
      return {
        ...model,
        status: action.value,
      };
  }
};

export type Props = ChildProps<Model, Action>;

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;
  const { activity } = useTenantStore(state => state.getAllEntities());
  return (
    <div className="flex flex-col gap-2">
      <Input
        type="text"
        label="Activity Name"
        field={model.name}
        onChange={flow(NameChanged, dispatch)}
      />

      <div className="flex flex-1 flex-row gap-4">
        <Input
          type="date"
          label="Start Date"
          field={model.startDate}
          onChange={flow(StartDateChanged, dispatch)}
          className="flex-1"
        />
        <Input
          type="date"
          label="End Date"
          field={model.endDate}
          onChange={flow(EndDateChanged, dispatch)}
          className="flex-1"
        />
      </div>
      {activity.attributes?.status?.visible && (
        <Select
          label="Activity Status"
          options={activityStatusOptions}
          renderLabel={stringLabel}
          optionKey={identity}
          selected={O.some(model.status)}
          onSelected={flow(
            O.getOrElse(() => ActivityStatus.NotStarted),
            StatusChanged,
            dispatch
          )}
        />
      )}
    </div>
  );
}
