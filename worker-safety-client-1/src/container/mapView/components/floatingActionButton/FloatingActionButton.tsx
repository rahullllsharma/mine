import type { IconName } from "@urbint/silica";
import type { ButtonProps } from "@/components/shared/button/Button";
import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import Button from "@/components/shared/button/Button";

type FloatingActionButtonProps = PropsWithClassName<{
  label?: string;
  icon: IconName;
}> &
  Pick<ButtonProps, "onClick">;

/**
 * This could be extended to be the actual FAB
 *
 * It's missing a couple of features, like positioning, because this was only done for the context of this
 * map. If we need to promote this into a global component, we should that that into account.
 */
function FloatingActionButton({
  label,
  icon,
  className,
  onClick,
}: FloatingActionButtonProps) {
  return (
    <Button
      label={label}
      iconStart={icon}
      className={cx(
        `absolute bottom-4 right-4 z-20 py-2 px-4 rounded-full
          text-brand-urbint-50 text-sm bg-white font-semibold shadow-20`,
        className
      )}
      onClick={onClick}
    />
  );
}

export { FloatingActionButton };
