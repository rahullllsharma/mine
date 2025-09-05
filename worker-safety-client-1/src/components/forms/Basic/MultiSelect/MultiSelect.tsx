import type { Eq } from "fp-ts/lib/Eq";
import { Icon } from "@urbint/silica";
import { throttle } from "lodash-es";
import classnames from "classnames";
import { useOnClickOutside } from "usehooks-ts";
import { useCallback, useMemo, useRef, useState } from "react";
import * as A from "fp-ts/lib/Array";
import * as O from "fp-ts/lib/Option";
import { flow, pipe } from "fp-ts/lib/function";
import { EmptyOption, SelectOption, stringLabel } from "../SelectOption";
import styles from "./MultiSelect.module.css";
import { Tag } from "./Tag";

type Opt<L, V> = {
  label: L;
  value: V;
};

export type MultiSelectProps<L, V> = {
  id?: string;
  className?: string;
  label?: string;
  labelClassName?: string;
  placeholder?: string;
  typeahead?: boolean;
  options: Opt<L, V>[];
  selected: V[];
  valueEq?: Eq<V>;
  disabled?: boolean;
  hasError?: boolean;
  renderLabel: (label: L) => string;
  optionKey: (value: V) => string;
  onSelected: (value: V) => void;
  onRemoved: (value: V) => void;
  closeOnOutsideClick?: boolean;
};

function MultiSelect<L, V>({
  id,
  className,
  label,
  labelClassName,
  placeholder = "Select an option",
  typeahead = false,
  options,
  selected,
  valueEq,
  disabled,
  hasError = false,
  renderLabel,
  optionKey,
  onSelected,
  onRemoved,
  closeOnOutsideClick = true,
}: MultiSelectProps<L, V>) {
  const ref = useRef(null);
  const [search, setSearch] = useState("");
  const listedOptions = useMemo(
    () =>
      search.length > 0
        ? pipe(
            options,
            A.filter(option =>
              renderLabel(option.label)
                .toLowerCase()
                .includes(search.toLowerCase())
            )
          )
        : options,
    [options, renderLabel, search]
  );

  const [isOpen, setIsOpen] = useState(false);

  const onOutsideClick = () => closeOnOutsideClick && setIsOpen(false);

  useOnClickOutside(ref, onOutsideClick);

  const toggleOpen = throttle((val: O.Option<boolean>) => {
    if (disabled) return;
    pipe(
      val,
      O.fold(
        () => setIsOpen(!isOpen),
        v => setIsOpen(v)
      )
    );
  }, 200);

  const isSomethingSelected = selected.length > 0;

  const isOptionSelected = useCallback(
    (value: V) => {
      if (valueEq) {
        return pipe(selected, A.elem(valueEq)(value));
      } else {
        return selected.includes(value);
      }
    },
    [selected, valueEq]
  );

  const selectedOptions = useMemo(() => {
    if (valueEq) {
      return pipe(
        options,
        A.filter(option => pipe(selected, A.elem(valueEq)(option.value)))
      );
    } else {
      return options.filter(option => selected.includes(option.value));
    }
  }, [options, selected, valueEq]);

  const onOptionSelected = useCallback(
    (value: V) => {
      setSearch("");
      if (isOptionSelected(value)) {
        onRemoved(value);
      } else {
        onSelected(value);
      }
    },
    [onSelected, onRemoved, isOptionSelected]
  );

  const onEmptyOptionSelected = useCallback(() => {
    setIsOpen(false);
    setSearch("");
  }, []);

  if (!isOpen && search !== "") {
    setSearch("");
  }

  return (
    <>
      <div ref={ref} id={id} className={classnames("w-full", className)}>
        {label && (
          <span
            className={classnames(
              "text-sm text-brand-gray-70 font-semibold w-full",
              labelClassName
            )}
          >
            {label}
          </span>
        )}
        <div
          aria-hidden="true"
          tabIndex={0}
          role="select"
          className={classnames(styles.select, {
            [styles.selectPlaceholder]: !isSomethingSelected || disabled,
            [styles.selectError]: hasError,
          })}
          onKeyUp={(e: React.KeyboardEvent<HTMLDivElement>) =>
            e.key === "Enter" && toggleOpen(O.none)
          }
          onClick={() => toggleOpen(O.none)}
        >
          {isSomethingSelected ? (
            <div className="flex flex-wrap flex-row flex-grow gap-1">
              {selectedOptions.map(option => (
                <Tag
                  key={optionKey(option.value)}
                  label={renderLabel(option.label)}
                  removeTestId={`${option.value}-remove`}
                  disabled={disabled}
                  onDeleteClick={event => {
                    onRemoved(option.value);
                    event.stopPropagation();
                  }}
                />
              ))}
              {typeahead ? (
                <div className="flex flex-grow">
                  <input
                    type="text"
                    className="w-full outline-none"
                    value={search}
                    disabled={disabled}
                    onChange={evt => setSearch(evt.target.value)}
                  />
                </div>
              ) : (
                <div className="flex flex-grow cursor-pointer"></div>
              )}
            </div>
          ) : (
            <div className="flex flex-grow cursor-pointer">
              {typeahead ? (
                <input
                  type="text"
                  placeholder={placeholder}
                  className="w-full outline-none"
                  value={search}
                  disabled={disabled}
                  onChange={evt => setSearch(evt.target.value)}
                />
              ) : (
                <div className="flex flex-1 flex-row">
                  <span className="truncate">{placeholder}</span>
                </div>
              )}
            </div>
          )}
          <div
            className="flex items-center cursor-pointer"
            onClick={() => toggleOpen(O.none)}
          >
            <Icon
              name={isOpen ? "chevron_up" : "chevron_down"}
              className="text-base self-center ml-2 cursor-pointer"
              onClick={() => toggleOpen(O.none)}
            />
          </div>
        </div>
        {isOpen && (
          <ul className="bg-white max-h-36 overflow-y-auto mt-2 rounded border-solid border-[1px] border-brand-gray-40">
            {listedOptions.length > 0 ? (
              listedOptions.map(option => {
                return (
                  <SelectOption
                    key={optionKey(option.value)}
                    option={option}
                    isSelected={isOptionSelected}
                    renderLabel={flow(renderLabel, stringLabel)}
                    onClick={onOptionSelected}
                  />
                );
              })
            ) : (
              <EmptyOption
                label="No options available"
                onClick={onEmptyOptionSelected}
              />
            )}
          </ul>
        )}
      </div>
    </>
  );
}

export { MultiSelect };
