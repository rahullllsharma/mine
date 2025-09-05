import React, { useState } from "react";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import RichtextEditor from "../shared/field/fieldTextEditor/FieldTextEditor";

const RichText: React.FC = () => {
  const [state, setState] = useState<string>("");
  return (
    <div className=" flex flex-col p-5">
      <div className="flex items-center text-neutral-shade-100 font-semibold justify-between mb-4">
        <h6>Add Question</h6>

        <ButtonIcon
          iconName="close_big"
          className="leading-5"
          onClick={() => {
            console.log();
          }}
          title="Close "
        />
      </div>
      <div>
        <RichtextEditor onChange={e => setState(e)} value={state} />
      </div>
      <div className="flex self-end  flex-row-reverse m-4">
        <ButtonPrimary
          label={"Add"}
          onClick={() => {
            console.log();
          }}
        />
        <ButtonRegular
          className="mr-2"
          label="Cancel"
          onClick={() => {
            console.log();
          }}
        />
      </div>
    </div>
  );
};

export default RichText;
