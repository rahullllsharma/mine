import type { FormField } from "@/utils/formField";
import type * as tt from "io-ts-types";
import type * as t from "io-ts";
import type { ChildProps } from "@/utils/reducerWithEffect";
import { flow } from "fp-ts/lib/function";
import { nonEmptyStringCodec } from "@/utils/validation";
import { fieldDef, setDirty } from "@/utils/formField";
import { Input } from "../Basic/Input";

export const formDefinition = {
  name: fieldDef(nonEmptyStringCodec().decode),
};

export type Model = {
  name: FormField<t.Errors, string, tt.NonEmptyString>;
};

export const init = (defaultName: string): Model => ({
  name: formDefinition.name.init(defaultName),
});

export const withDirtyForm = (model: Model): Model => ({
  ...model,
  name: setDirty(model.name),
});

export type Action = {
  type: "NameChanged";
  value: string;
};

export const NameChanged = (value: string): Action => ({
  type: "NameChanged",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "NameChanged":
      return {
        ...model,
        name: formDefinition.name.update(action.value),
      };
  }
};

export type Props = ChildProps<Model, Action>;

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;

  return (
    <div className="flex flex-col gap-2">
      <Input
        type="text"
        label="Activity Name"
        field={model.name}
        onChange={flow(NameChanged, dispatch)}
      />
    </div>
  );
}
