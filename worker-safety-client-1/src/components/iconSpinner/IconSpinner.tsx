import { Icon } from "@urbint/silica";
import cx from "classnames";

type IconSpinnerProps = {
  className?: string;
  testId?: string;
};

function IconSpinner({ className }: IconSpinnerProps): JSX.Element {
  return <Icon name="uploading" className={cx("animate-spin", className)} />;
}

export { IconSpinner };
