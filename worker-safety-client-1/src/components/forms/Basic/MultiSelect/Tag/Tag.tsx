import type { MouseEventHandler } from "react";
import { Icon } from "@urbint/silica";
import { constVoid } from "fp-ts/lib/function";

export type TagProps = {
  label: string;
  removeTestId?: string;
  disabled?: boolean;
  onDeleteClick: MouseEventHandler;
};

function Tag({
  label,
  removeTestId = "remove-tag",
  disabled,
  onDeleteClick,
}: TagProps): JSX.Element {
  return (
    <div
      aria-hidden="true"
      className="w-fit text-base gap-1 flex justify-between px-[6px] py-1 bg-brand-urbint-10 border-solid border-[1px] rounded-md border-brand-urbint-30"
    >
      <span className="text-neutral-shade-100">{label}</span>
      {!disabled && (
        <Icon
          data-testid={removeTestId}
          className="self-center text-neutral-shade-38 cursor-pointer"
          onClick={disabled ? constVoid : onDeleteClick}
          name="off_outline_close"
        />
      )}
    </div>
  );
}

export { Tag };
