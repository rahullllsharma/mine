import type { Option } from "fp-ts/lib/Option";
import type { Eq } from "fp-ts/lib/Eq";
import * as O from "fp-ts/lib/Option";
import { isSome } from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import { Icon } from "@urbint/silica";
import classnames from "classnames";
import { useCallback, useMemo, useRef, useState, useEffect } from "react";
import { useOnClickOutside } from "usehooks-ts";
import { flow, pipe } from "fp-ts/lib/function";
import { EmptyOption, SelectOption, stringLabel } from "../SelectOption";
import styles from "./Select.module.css";

type Opt<L, V> = {
  label: L;
  value: V;
};

export type SelectProps<L, V> = {
  id?: string;
  className?: string;
  labelClassName?: string;
  label?: string;
  placeholder?: string;
  options: Opt<L, V>[];
  selected: Option<V>;
  valueEq?: Eq<V>;
  disabled?: boolean;
  hasError?: boolean;
  onSelected: (value: Option<V>) => void;
  renderLabel: (label: L) => JSX.Element;
  typeaheadOptionLabel?: (label: L) => string;
  optionKey: (value: V) => string;
  closeOnOutsideClick?: boolean;
};

function Select<L, V>({
  id,
  className,
  label,
  labelClassName,
  placeholder = "Select an option",
  options,
  selected,
  valueEq,
  disabled,
  hasError = false,
  renderLabel,
  typeaheadOptionLabel,
  optionKey,
  onSelected,
  closeOnOutsideClick = true,
}: SelectProps<L, V>) {
  const ref = useRef<HTMLDivElement>(null);
  const divRef = useRef<HTMLDivElement>(null);
  const [search, setSearch] = useState("");
  const [dropdownDirectionUp, setDropdownDirectionUp] = useState(false);

  const listedOptions = useMemo(() => {
    if (typeaheadOptionLabel) {
      return search.length > 0
        ? pipe(
            options,
            A.filter(option =>
              typeaheadOptionLabel(option.label)
                .toLowerCase()
                .includes(search.toLowerCase())
            )
          )
        : options;
    }
    return options;
  }, [options, typeaheadOptionLabel, search]);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (open && divRef.current) {
      const dropdownRect = divRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - dropdownRect.bottom;
      const spaceAbove = dropdownRect.top;
      if (spaceBelow < 200 && spaceAbove > spaceBelow)
        setDropdownDirectionUp(true);
      else setDropdownDirectionUp(false);
    }
  }, [open]);
  const onClickOutside = () => closeOnOutsideClick && setOpen(false);
  useOnClickOutside(ref, onClickOutside);

  const isOptionSelected = useCallback(
    (value: V) => {
      if (valueEq !== null && valueEq !== undefined) {
        return O.getEq(valueEq).equals(selected, O.some(value));
      } else {
        return isSome(selected) && value === selected.value;
      }
    },
    [selected, valueEq]
  );
  const selectedOption = useMemo(
    () => options.find(option => isOptionSelected(option.value)),
    [options, isOptionSelected]
  );

  const onOptionSelected = useCallback(
    (value: Option<V>) => {
      onSelected(value);
      setSearch("");
      setOpen(false);
    },
    [onSelected]
  );

  const toggleOpen = useCallback(() => {
    if (!disabled) {
      if (!open) setSearch("");
      setOpen(!open);
    }
  }, [open, disabled]);

  if (!open && search !== "") {
    setSearch("");
  }

  return (
    <div ref={ref} className={classnames("relative", className)} id={id}>
      {label && (
        <span
          className={classnames(
            "text-sm text-brand-gray-70 font-semibold pointer-events-none",
            labelClassName
          )}
        >
          {label}
        </span>
      )}
      <div onClick={toggleOpen}>
        <div
          ref={divRef}
          aria-hidden="true"
          tabIndex={0}
          role="select"
          className={classnames(styles.select, {
            [styles.selectPlaceholder]: !selectedOption || disabled,
            [styles.selectError]: hasError,
          })}
          onKeyUp={(e: React.KeyboardEvent<HTMLDivElement>) =>
            e.key === "Enter" && toggleOpen()
          }
        >
          {selectedOption ? (
            <div className="flex flex-wrap flex-row flex-grow gap-1">
              {typeaheadOptionLabel ? (
                <>
                  {search.length === 0 && renderLabel(selectedOption.label)}
                  <div className="flex flex-grow cursor-pointer">
                    <input
                      type="text"
                      className="w-full outline-none"
                      value={search}
                      disabled={disabled}
                      onChange={evt => setSearch(evt.target.value)}
                      onFocus={toggleOpen}
                    />
                  </div>
                </>
              ) : (
                <div
                  className="flex flex-grow cursor-pointer"
                  onClick={toggleOpen}
                >
                  {renderLabel(selectedOption.label)}
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-grow cursor-pointer">
              {typeaheadOptionLabel ? (
                <input
                  type="text"
                  placeholder={placeholder}
                  className="w-full outline-none"
                  value={search}
                  disabled={disabled}
                  onChange={evt => setSearch(evt.target.value)}
                  onFocus={toggleOpen}
                />
              ) : (
                <div className="flex flex-1 flex-row" onClick={toggleOpen}>
                  <span className="truncate">{stringLabel(placeholder)}</span>
                </div>
              )}
            </div>
          )}

          <Icon
            name={open ? "chevron_up" : "chevron_down"}
            className="text-base self-center cursor-pointer"
            onClick={toggleOpen}
          />
        </div>

        {open && (
          <ul
            className={classnames(
              dropdownDirectionUp
                ? "bg-white w-full max-h-36 overflow-y-auto mb-2 rounded border-solid border-[1px] border-brand-gray-40 absolute bottom-full"
                : "bg-white max-h-36 overflow-y-auto mt-2 rounded border-solid border-[1px] border-brand-gray-40"
            )}
          >
            <EmptyOption
              key={""}
              label={placeholder}
              onClick={() => onOptionSelected(O.none)}
            />
            {listedOptions.map(option => (
              <SelectOption
                key={optionKey(option.value)}
                option={option}
                isSelected={isOptionSelected}
                renderLabel={renderLabel}
                onClick={flow(O.some, onOptionSelected)}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export { Select };
