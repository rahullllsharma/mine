import type { PropsWithClassName } from "@/types/Generic";

import cx from "classnames";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";

export type PageFooterProps = PropsWithClassName<{
  primaryActionLabel?: string;
  onPrimaryClick?: () => void;
  isPrimaryActionDisabled?: boolean;
  isPrimaryActionLoading?: boolean;
}>;

export default function PageFooter({
  className,
  primaryActionLabel,
  onPrimaryClick,
  isPrimaryActionDisabled,
  isPrimaryActionLoading,
}: PageFooterProps): JSX.Element {
  return (
    <footer className={cx("flex items-center p-2 bg-brand-gray-10", className)}>
      <div className="flex flex-1 justify-end">
        {onPrimaryClick && (
          <ButtonPrimary
            onClick={onPrimaryClick}
            label={primaryActionLabel}
            disabled={isPrimaryActionDisabled}
            loading={isPrimaryActionLoading}
          />
        )}
      </div>
    </footer>
  );
}
