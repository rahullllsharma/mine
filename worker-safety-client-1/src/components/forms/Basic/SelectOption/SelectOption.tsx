import { Icon } from "@urbint/silica";
import classnames from "classnames";

import styles from "./SelectOption.module.css";

export function stringLabel(label: string): JSX.Element {
  return <span>{label}</span>;
}

export type SelectOptionProps<L, V> = {
  option: { label: L; value: V };
  isSelected: (_: V) => boolean;
  renderLabel: (label: L) => JSX.Element;
  onClick: (raw: V) => void;
};

function SelectOption<L, V>({
  option,
  onClick,
  renderLabel,
  isSelected,
}: SelectOptionProps<L, V>): JSX.Element {
  const selected = isSelected(option.value);

  return (
    <li
      aria-hidden="true"
      onClick={() => onClick(option.value)}
      className={classnames(styles.option, {
        [styles.selected]: selected,
      })}
    >
      {renderLabel(option.label)}
      {selected && <Icon name="check" />}
    </li>
  );
}

export type EmptyOptionProps = {
  label: string;
  onClick: () => void;
};

export function EmptyOption({ onClick, label }: EmptyOptionProps): JSX.Element {
  return (
    <li
      aria-hidden="true"
      onClick={onClick}
      className={classnames(styles.option, styles.selectPlaceholder)}
    >
      {label}
    </li>
  );
}

export { SelectOption };
