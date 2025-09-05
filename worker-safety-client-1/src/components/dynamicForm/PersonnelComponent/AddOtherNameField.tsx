import { useState } from "react";
import { v4 as uuid } from "uuid";
import { Icon } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";

export interface AddOtherNameFieldProps {
  onSave: (row: { id: string; name: string }) => void;
}

const AddOtherNameField = ({ onSave }: AddOtherNameFieldProps) => {
  const [isAdding, setIsAdding] = useState(false);
  const [value, setValue] = useState("");

  const reset = () => {
    setValue("");
    setIsAdding(false);
  };

  const commit = () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    const id = `other-${uuid()}`;
    onSave({ id, name: trimmed });
    setValue("");
    setIsAdding(false);
  };

  if (!isAdding) {
    return (
      <ButtonTertiary
        label="Add Other Name"
        size="sm"
        onClick={() => setIsAdding(true)}
        className="text-brand-urbint-40 w-fit bg-transparent"
      />
    );
  }

  return (
    <div className="flex items-center">
      <InputRaw
        type="text"
        placeholder="Enter other name"
        value={value}
        onChange={setValue}
      />
      <ButtonSecondary className="ml-2" onClick={reset}>
        <Icon name="close_big" />
      </ButtonSecondary>
      <ButtonPrimary className="ml-1" onClick={commit} disabled={!value.trim()}>
        <Icon name="check_bold" />
      </ButtonPrimary>
    </div>
  );
};

export default AddOtherNameField;
