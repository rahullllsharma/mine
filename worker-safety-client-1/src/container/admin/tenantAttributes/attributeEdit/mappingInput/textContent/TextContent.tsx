import { useState, useRef } from "react";
import { Icon } from "@urbint/silica";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Input from "@/components/shared/input/Input";
import Tooltip from "@/components/shared/tooltip/Tooltip";

type TextContentProps = {
  label: string;
  defaultLabel: string;
  isDefault?: boolean;
  onSubmit: (label: string) => void;
  onEditOpen?: () => void;
  onEditClose?: () => void;
};

const TextContent = ({
  label,
  defaultLabel,
  isDefault,
  onSubmit,
  onEditOpen,
  onEditClose,
}: TextContentProps): JSX.Element => {
  /* TODO:
   * Investigate the possibility to convert this component to use only an input element
   * with the readOnly prop controlling it's aspect.
   * And also wrap the input element in RHF.
   */

  const [isEditMode, setIsEditMode] = useState(false);
  const inputField = useRef<HTMLInputElement>(null);

  const isTooltipVisible = label !== defaultLabel;

  if (isEditMode) {
    return (
      <>
        <Input ref={inputField} defaultValue={label} />
        <ButtonPrimary
          iconStart="check_bold"
          className="flex-shrink-0"
          onClick={() => {
            onSubmit(inputField.current?.value || "");
            setIsEditMode(previousValue => !previousValue);
            onEditClose?.();
          }}
        />
        <ButtonSecondary
          iconStart="close_big"
          className="flex-shrink-0"
          onClick={() => {
            setIsEditMode(previousValue => !previousValue);
            onEditClose?.();
          }}
        />
      </>
    );
  }

  const fullLabelText = isDefault ? `${label} (default)` : label;

  return (
    <>
      <div className="flex-grow flex gap-2">
        {fullLabelText}
        {isTooltipVisible && (
          <Tooltip
            title={`Original value: "${defaultLabel}"`}
            position="top"
            containerClasses="flex"
          >
            <Icon
              name="info_circle"
              className="text-xl leading-5"
              aria-label="mapping-tooltip"
            />
          </Tooltip>
        )}
      </div>
      <ButtonIcon
        iconName="edit"
        className="p-1"
        onClick={() => {
          setIsEditMode(previousValue => !previousValue);
          onEditOpen?.();
        }}
      />
    </>
  );
};

export { TextContent };
