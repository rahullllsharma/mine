import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useMemo, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter } from "@/components/dynamicForm/index";
import { Checkbox } from "../forms/Basic/Checkbox";

type ResponseOption = "slider" | "sliderText";

interface FormState {
  question: string;
  responseOption: ResponseOption;
  startDefault: number;
  min: number;
  max: number;
  increment: number;
  unitType: string;
  mandatory: boolean;
  comments: boolean;
  attachment: boolean;
  user_value: boolean | null;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const responseOptions: RadioGroupOption[] = [
  { id: 1, value: "slider", description: "Slider only" },
  { id: 2, value: "sliderText", description: "Slider with text input" },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const validateForm = (state: FormState): boolean => {
  let isValid = false;
  if (
    state.question &&
    state.min.toString() &&
    state.max.toString() &&
    state.increment.toString() &&
    state.startDefault.toString()
  ) {
    isValid = true;
  }
  return isValid;
};
const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      question: "",
      responseOption: "slider",
      startDefault: 1,
      min: 1,
      max: 20,
      increment: 1,
      unitType: "",
      mandatory: false,
      comments: false,
      attachment: false,
      user_value: null,
      user_comments: null,
      user_attachments: null,
    }
  );

  const handleInputChange = (name: keyof FormState, value: any) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);
  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question *"
          placeholder="Enter your question"
          value={formState.question}
          onChange={e => handleInputChange("question", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Response type"
          options={responseOptions}
          defaultOption={responseOptions[0]}
          onSelect={response => handleInputChange("responseOption", response)}
          readOnly={props.disabled}
        />
        <div className="flex justify-between gap-4">
          <InputRaw
            label="Start/Defualt *"
            placeholder="3"
            type="number"
            value={formState.startDefault.toString()}
            onChange={e => handleInputChange("startDefault", e)}
            disabled={props.disabled}
          />
          <InputRaw
            label="Min *"
            placeholder="0"
            type="number"
            value={formState.min.toString()}
            onChange={e => handleInputChange("min", e)}
            disabled={props.disabled}
          />
          <InputRaw
            label="Max *"
            placeholder="20"
            type="number"
            value={formState.max.toString()}
            onChange={e => handleInputChange("max", e)}
            disabled={props.disabled}
          />
        </div>
        <div className="flex gap-4">
          <InputRaw
            label="Increment*"
            placeholder="20"
            type="number"
            value={formState.increment.toString()}
            onChange={e => handleInputChange("increment", e)}
            disabled={props.disabled}
          />
          <InputRaw
            label="Unit type"
            placeholder="Inch, cm, miles"
            value={formState.unitType.toString()}
            onChange={e => handleInputChange("unitType", e)}
            disabled={props.disabled}
          />
          <span style={{ width: "100%" }} />
        </div>
        <div className="border-gray-200 border-t divide-brand-gray-2 pb-4 flex justify-between gap-4 pt-6">
          <Checkbox
            checked={formState.mandatory}
            onClick={() => handleInputChange("mandatory", !formState.comments)}
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Mandatory</span>
          </Checkbox>
          <Checkbox
            checked={formState.comments}
            onClick={() => handleInputChange("comments", !formState.comments)}
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Comments</span>
          </Checkbox>
          <Checkbox
            checked={formState.attachment}
            onClick={() =>
              handleInputChange("attachment", !formState.attachment)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Attachment</span>
          </Checkbox>
        </div>
      </div>
      <Foooter
        onAdd={props.onAdd}
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
