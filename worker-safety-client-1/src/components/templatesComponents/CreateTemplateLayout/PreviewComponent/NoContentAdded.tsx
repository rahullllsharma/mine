import React, { useContext } from "react";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import style from "../createTemplateStyle.module.scss";
import { ModeTypePageSection } from "../../customisedForm.types";

type NoContentAddedType = {
  setIsOpen: (item: boolean) => void;
  setMode: (item: ModeTypePageSection) => void;
};
const NoContentAdded = ({ setIsOpen, setMode }: NoContentAddedType) => {
  const { state } = useContext(CustomisedFromStateContext)!;

  return (
    <div className={style.noContentAddedStyle}>
      {!state.form.contents.length ? (
        <>
          <h4>No Pages added</h4>
          <p>
            Click on
            <ButtonIcon
              iconName="plus_square"
              onClick={() => {
                setMode("addPage");
              }}
            />
            to add a new page
          </p>
        </>
      ) : (
        <>
          <h4>No content added</h4>
          <p>
            Click on
            <ButtonIcon
              iconName="plus_square"
              onClick={() => {
                setIsOpen(true);
              }}
            />
            to add a new content
          </p>
        </>
      )}
    </div>
  );
};

export default NoContentAdded;
