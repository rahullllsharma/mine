import classnames from "classnames";

import styles from "./Toggle.module.css";

export type ToggleProps = {
  className?: string;
  checked: boolean;
  disabled?: boolean;
  containerStyle?: string;
  onClick: () => void;
  htmlFor?: string;
};

function Toggle({
  className,
  checked,
  disabled,
  onClick,
  containerStyle,
}: ToggleProps) {
  return (
    <>
      <div onClick={onClick} className={containerStyle}>
        <input
          className={styles.inputCheckbox}
          type="checkbox"
          checked={checked}
          disabled={disabled}
          readOnly
        />
        <label className={classnames(styles.toggle, className)} />
      </div>
    </>
  );
}

export { Toggle };
