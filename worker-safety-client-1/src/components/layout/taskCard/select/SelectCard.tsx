import type { PropsWithClassName } from "@/types/Generic";
import type { FieldSearchSelectProps } from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import cx from "classnames";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import UserAvatar from "@/components/shared/avatar/user/UserAvatar";
import UserAddedLabel from "./UserAddedLabel";

export type SelectCardProps = FieldSearchSelectProps &
  PropsWithClassName<{
    userInitials: string;
    type: SelectCardType;
    isDisabled?: boolean;
    onRemove?: () => void;
  }>;

export type SelectCardOption = InputSelectOption & {
  isSelected?: boolean;
};

export type SelectCardType = "hazard" | "control";

export default function SelectCard({
  userInitials,
  type,
  isDisabled,
  onRemove,
  className = "",
  ...fieldProps
}: SelectCardProps): JSX.Element {
  const { defaultOption } = fieldProps;
  const dynamicStyles = {
    ["border border-dashed border-brand-gray-30 rounded"]: type === "control",
    ["p-3"]: type === "control",
    ["py-3 pr-3"]: type === "hazard",
  };

  const isRemoveVisible = onRemove && !isDisabled;

  return (
    <div
      className={cx(
        "flex items-center justify-between text-base text-neutral-shade-100",
        className,
        dynamicStyles
      )}
      data-testid="ControlSelectCard"
    >
      {isDisabled ? (
        <Paragraph text={defaultOption?.name} />
      ) : (
        <FieldSearchSelect
          defaultOption={defaultOption}
          size="sm"
          className="w-full md:w-8/12 mr-4"
          {...fieldProps}
        />
      )}
      <div className="flex items-center justify-center">
        <UserAvatar
          name={userInitials}
          className="mr-4 ml-1.5 relative"
          hoverElement={
            <UserAddedLabel
              className="absolute top-0 right-8"
              label={`User added ${type}`}
            />
          }
        />
        {isRemoveVisible && (
          <ButtonIcon
            iconName="trash_empty"
            className="leading-5"
            onClick={onRemove}
            aria-label="remove"
          />
        )}
      </div>
    </div>
  );
}
