import type { ChildProps } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/Option";
import type { Ebo } from "@/api/codecs";
import type { StepSnapshot } from "../Utils";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/Option";
import { pipe } from "fp-ts/lib/function";
import StepLayout from "@/components/forms/StepLayout";
import { FieldGroup } from "@/components/shared/FieldGroup";

export type Model = {
  notes: string;
};

export function init(ebo: Option<Ebo>): Model {
  const eboContents = pipe(
    ebo,
    O.map(e => e.contents)
  );

  return {
    notes: pipe(
      eboContents,
      O.chain(c => c.additionalInformation),
      O.fold(
        () => "",
        s => s
      )
    ),
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return { notes: model.notes };
};

export const toSaveEboInput = (model: Model) => {
  return E.of({ additionalInformation: model.notes });
};

export type Action = { type: "NotesChanged"; value: string };

export const NotesChanged = (value: string): Action => ({
  type: "NotesChanged",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "NotesChanged":
      return { ...model, notes: action.value };
  }
};

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  return (
    <StepLayout>
      <FieldGroup legend="Additional Information">
        <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold leading-normal">
          Comments
        </label>
        <textarea
          className="w-full h-24 p-2 border-solid border-[1px] border-brand-gray-40 rounded"
          value={model.notes}
          onChange={e => pipe(e.target.value, NotesChanged, dispatch)}
          disabled={isReadOnly}
        />
      </FieldGroup>
    </StepLayout>
  );
}

export default View;
