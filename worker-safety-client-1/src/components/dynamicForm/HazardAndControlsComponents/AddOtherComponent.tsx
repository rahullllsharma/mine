import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

function AddOtherComponent({
  showOther,
  setShowOther,
  onAdd,
  placeholder,
}: {
  showOther: boolean;
  setShowOther: (value: boolean) => void;
  placeholder: string;
  onAdd: (value: {
    id: string;
    name: string;
    isUserAdded: boolean;
    isApplicable: boolean;
  }) => void;
}) {
  const [value, setValue] = useState("");

  const onTextBoxChange = (enteredValue: string) => {
    setValue(enteredValue);
  };

  const onUserAddingValue = (name: string) => {
    onAdd({
      id: uuidv4(),
      name: name,
      isUserAdded: true,
      isApplicable: false,
    });
    setValue("");
  };

  return (
    <>
      <div className="pt-3">
        <div className="pt-1" onClick={() => setShowOther(true)}>
          <span className="text-brand-urbint-40 font-semibold text-sm cursor-pointer">
            Other (please specify)
          </span>
        </div>
        {showOther && (
          <div className="flex mt-2">
            <div className="flex md:flex-col w-full">
              <InputRaw
                onChange={onTextBoxChange}
                value={value}
                placeholder={placeholder}
              />
            </div>
            <div className="flex justify-end ml-2">
              <ButtonIcon
                iconName="close_small"
                onClick={() => {
                  setShowOther(false);
                  setValue("");
                }}
                className="bg-white text-black border-[1px] border-gray-300 pl-3 pr-3 rounded-md mr-2"
              />

              <ButtonIcon
                iconName="check"
                disabled={value.trim().length == 0}
                onClick={() => onUserAddingValue(value)}
                className="text-backgrounds-white bg-brand-urbint-40 pl-3 pr-3 rounded-md"
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default AddOtherComponent;
