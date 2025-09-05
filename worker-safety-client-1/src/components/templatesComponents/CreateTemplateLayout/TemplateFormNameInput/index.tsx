import React, { useContext, useEffect, useRef, useState } from "react";
import { trim } from "lodash-es";
import { useRouter } from "next/router";
import { BodyText } from "@urbint/silica";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Input from "@/components/shared/input/Input";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import style from "../createTemplateStyle.module.scss";

const TemplateFormNameInput = () => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const [newFormName, setNewFormName] = useState<string>("");
  const router = useRouter();
  const { templateId } = router.query;

  const [showTextbox, setShowTextbox] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (templateId) {
      setShowTextbox(false);
    } else {
      setShowTextbox(true);
    }
  }, [templateId]);

  const inputRef = useRef<HTMLInputElement>(null);
  const toastCtx = useContext(ToastContext);

  useEffect(() => {
    setNewFormName(state.form.properties.title);
  }, [state.form.properties.title]);

  useEffect(() => {
    if (showTextbox && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showTextbox]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (
      value.length > 100 &&
      value.length - newFormName.length === 1 &&
      value.startsWith(newFormName)
    ) {
      return;
    }
    setNewFormName(value);
    setError("");
  };

  const handlePaste = (_e: React.ClipboardEvent<HTMLInputElement>) => {
    // Allow pasting any length, do not block or trim
    // No action needed
  };

  const handleEditButtonClick = () => {
    setShowTextbox(true);
    inputRef?.current?.focus();
  };

  const handleSaveButtonClick = () => {
    if (!newFormName || !trim(newFormName)) {
      setNewFormName("");
      toastCtx?.pushToast("error", "Template Name cannot be empty");
      return;
    }
    if (newFormName.length > 100) {
      setError("Template name must be 100 characters or fewer.");
      return;
    }
    setShowTextbox(false);
    dispatch({
      type: CF_REDUCER_CONSTANTS.FORM_NAME_CHANGE,
      payload: newFormName,
    });
    toastCtx?.pushToast(
      "success",
      "Template Name Edited. Make sure to tap Save/Publish button to keep your changes intact"
    );
  };

  const handleCancelButtonClick = () => {
    setShowTextbox(true);
    setNewFormName("");
    setError("");
  };

  return (
    <div className={style.formNameInputParent}>
      {showTextbox ? (
        <div className="relative w-full flex flex-col gap-1">
          <Input
            placeholder="Enter the form name *"
            value={newFormName}
            ref={inputRef}
            onChange={handleInputChange}
            onPaste={handlePaste}
            className="w-full pr-20 sm:pr-20 pl-3 py-2 text-base overflow-x-auto whitespace-nowrap"
            error={error}
          />
          {newFormName.length > 0 && (
            <div className="absolute right-3 top-[32%] -translate-y-1/2 flex items-center space-x-2 z-10">
              <ButtonIcon
                iconName="check_big"
                className="text-small"
                disabled={!!error || !newFormName}
                onClick={handleSaveButtonClick}
              />
              <ButtonIcon
                iconName="close_big"
                disabled={false}
                onClick={handleCancelButtonClick}
              />
            </div>
          )}
          {showTextbox && newFormName.length > 0 && !error && (
            <div className="flex flex-wrap items-center justify-between gap-2 mt-1 min-h-[1.25rem] w-full">
              <BodyText className="text-sm text-neutral-shade-58 pl-2 truncate max-w-[70vw] sm:max-w-[70%]">
                Click on ✔ icon to confirm the title name
              </BodyText>
              <BodyText
                className={`text-xs ${
                  newFormName.length >= 100
                    ? "text-red-500"
                    : newFormName.length >= 90
                    ? "text-yellow-500"
                    : "text-neutral-400"
                }`}
              >
                {newFormName.length}/100
              </BodyText>
            </div>
          )}
          {error && (
            <BodyText className="text-red-500 text-sm mt-1 block pl-2">
              {error}
            </BodyText>
          )}
        </div>
      ) : (
        <div
          style={{
            fontSize: "20px",
            marginLeft: "10px",
            marginTop: "4px",
            lineHeight: "30px",
            marginBottom: "12px",
            whiteSpace: "nowrap",
          }}
        >
          {newFormName}
          {!showTextbox && newFormName.length > 0 && (
            <ButtonIcon
              iconName="edit"
              className="ml-2"
              disabled={false}
              onClick={handleEditButtonClick}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default TemplateFormNameInput;
