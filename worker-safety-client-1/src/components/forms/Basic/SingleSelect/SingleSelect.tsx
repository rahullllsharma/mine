import { BodyText, Icon } from "@urbint/silica";
import classnames from "classnames";
import { useOnClickOutside } from "usehooks-ts";
import { useCallback, useMemo, useRef, useState, useEffect } from "react";
import Button from "../../../shared/button/Button";
import styles from "./SingleSelect.module.scss";

type Option = {
  label: string;
  value: string;
};

export type SingleSelectProps = {
  id?: string;
  className?: string;
  label?: string;
  labelClassName?: string;
  placeholder?: string;
  options: Option[];
  selected?: string;
  disabled?: boolean;
  hasError?: boolean;
  errorMessage?: string;
  onSelected: (value: string) => void;
  onClear?: () => void;
  closeOnOutsideClick?: boolean;
  showFullContent?: boolean;
};

function SingleSelect({
  id,
  className,
  label,
  labelClassName,
  placeholder = "Select an option",
  options,
  selected,
  disabled = false,
  hasError = false,
  errorMessage,
  onSelected,
  onClear,
  closeOnOutsideClick = true,
  showFullContent = false,
}: SingleSelectProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [isTyping, setIsTyping] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState<"below" | "above">(
    "below"
  );

  // Calculate dropdown position based on available space
  const calculateDropdownPosition = useCallback(() => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const isMobile = window.innerWidth <= 768;

    // Adjust dropdown height based on screen size
    const dropdownHeight = isMobile ? 200 : 240; // Smaller on mobile
    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;

    // Add some buffer for mobile to account for virtual keyboard
    const buffer = isMobile ? 20 : 0;

    // If there's not enough space below but enough space above, position above
    if (
      spaceBelow < dropdownHeight + buffer &&
      spaceAbove > dropdownHeight + buffer
    ) {
      setDropdownPosition("above");
    } else {
      setDropdownPosition("below");
    }
  }, []);

  // Filter options based on search
  const filteredOptions = useMemo(() => {
    if (search.length === 0) {
      return options.sort((a, b) => a.label.localeCompare(b.label));
    }

    return options
      .filter(option =>
        option.label.toLowerCase().includes(search.toLowerCase())
      )
      .sort((a, b) => a.label.localeCompare(b.label));
  }, [options, search]);

  // Handle outside click
  const onOutsideClick = () => {
    if (closeOnOutsideClick) {
      setIsOpen(false);
      setSearch("");
      setFocusedIndex(-1);
      setIsTyping(false);
    }
  };

  useOnClickOutside(ref, onOutsideClick);

  // Handle option selection
  const handleOptionSelect = useCallback(
    (value: string) => {
      onSelected(value);
      setIsOpen(false);
      setSearch("");
      setFocusedIndex(-1);
      setIsTyping(false);
    },
    [onSelected]
  );

  // Handle clear selection
  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onClear?.();
      setSearch("");
      setFocusedIndex(-1);
      setIsTyping(false);
    },
    [onClear]
  );

  // Handle input change
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearch(value);
      setIsOpen(true);
      setFocusedIndex(-1);
      setIsTyping(true);
    },
    []
  );

  // Handle textarea change
  const handleTextareaChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const value = e.target.value;
      setSearch(value);
      setIsOpen(true);
      setFocusedIndex(-1);
      setIsTyping(true);
    },
    []
  );

  // Handle input click
  const handleInputClick = useCallback(() => {
    if (!disabled) {
      const newIsOpen = !isOpen;
      setIsOpen(newIsOpen);

      if (newIsOpen) {
        if (showFullContent) {
          textareaRef.current?.focus();
        } else {
          inputRef.current?.focus();
        }
      }
    }
  }, [disabled, isOpen, showFullContent]);

  const handleDropdownArrowClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (!disabled) {
        setIsOpen(!isOpen);
      }
    },
    [disabled, isOpen]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (disabled) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          if (isOpen) {
            setFocusedIndex(prev =>
              prev < filteredOptions.length - 1 ? prev + 1 : 0
            );
          } else {
            setIsOpen(true);
          }
          break;
        case "ArrowUp":
          e.preventDefault();
          if (isOpen) {
            setFocusedIndex(prev =>
              prev > 0 ? prev - 1 : filteredOptions.length - 1
            );
          }
          break;
        case "Enter":
          e.preventDefault();
          if (
            isOpen &&
            focusedIndex >= 0 &&
            focusedIndex < filteredOptions.length
          ) {
            handleOptionSelect(filteredOptions[focusedIndex].value);
          } else if (!isOpen) {
            setIsOpen(true);
          }
          break;
        case "Escape":
          setIsOpen(false);
          setSearch("");
          setFocusedIndex(-1);
          if (showFullContent) {
            textareaRef.current?.blur();
          } else {
            inputRef.current?.blur();
          }
          break;
      }
    },
    [
      disabled,
      isOpen,
      focusedIndex,
      filteredOptions,
      handleOptionSelect,
      showFullContent,
    ]
  );

  // Get display value
  const displayValue = useMemo(() => {
    // Show search value when user is actively typing (even if empty)
    if (isTyping) return search;
    if (selected) {
      const selectedOption = options.find(option => option.value === selected);
      return selectedOption?.label || selected;
    }
    return "";
  }, [search, selected, options, isTyping]);

  // Highlight matching text
  const highlightText = useCallback((text: string, query: string) => {
    if (!query) return text;

    const regex = new RegExp(`(${query})`, "gi");
    const parts = text.split(regex);

    return parts.map((part, index) =>
      regex.test(part) ? (
        <strong key={index} className={styles.highlightedText}>
          {part}
        </strong>
      ) : (
        part
      )
    );
  }, []);

  // Reset search when component closes
  useEffect(() => {
    if (!isOpen && search) {
      setSearch("");
      setIsTyping(false);
    }
  }, [isOpen, search]);

  // Calculate dropdown position when opening
  useEffect(() => {
    if (isOpen) {
      calculateDropdownPosition();
    }
  }, [isOpen, calculateDropdownPosition, filteredOptions.length]);

  // Handle window resize to recalculate position
  useEffect(() => {
    const handleResize = () => {
      if (isOpen) {
        calculateDropdownPosition();
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [isOpen, calculateDropdownPosition, filteredOptions.length]);

  // Auto-resize textarea when content changes
  useEffect(() => {
    if (showFullContent && textareaRef.current) {
      const textarea = textareaRef.current;

      // Reset height to auto to get the natural height
      textarea.style.height = "auto";

      // Get the scroll height (natural height of content)
      const scrollHeight = textarea.scrollHeight;

      // Set minimum height based on screen size
      const isMobile = window.innerWidth <= 768;
      const minHeight = isMobile ? 40 : 36; // 2.5rem on mobile, 2.25rem on desktop
      const calculatedHeight = Math.max(scrollHeight, minHeight);

      // Set height to the calculated height
      textarea.style.height = `${calculatedHeight}px`;
    }
  }, [displayValue, showFullContent]);

  const isSelected = !!selected;
  const showClearButton = isSelected && !disabled;

  return (
    <div
      ref={ref}
      id={id}
      className={classnames(styles.singleSelectContainer, className)}
    >
      {label && (
        <label
          className={classnames(
            styles.label,
            { [styles.labelDisabled]: disabled },
            labelClassName
          )}
        >
          {label}
        </label>
      )}

      <div
        className={classnames(styles.inputContainer, {
          [styles.inputContainerError]: hasError,
          [styles.inputContainerDisabled]: disabled,
        })}
        onClick={handleInputClick}
      >
        {showFullContent ? (
          <textarea
            ref={textareaRef}
            id={id}
            name={id || "single-select-textarea"}
            value={displayValue}
            placeholder={!selected && !isTyping ? placeholder : ""}
            disabled={disabled}
            className={styles.textarea}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            autoComplete="off"
            rows={1}
          />
        ) : (
          <input
            ref={inputRef}
            id={id}
            name={id || "single-select-input"}
            type="text"
            value={displayValue}
            placeholder={!selected && !isTyping ? placeholder : ""}
            disabled={disabled}
            className={styles.input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            autoComplete="off"
          />
        )}

        <div className={styles.iconsContainer}>
          {showClearButton && (
            <Button
              type="button"
              className={styles.clearButton}
              onClick={handleClear}
              aria-label="Clear selection"
              iconStart="close_small"
              iconStartClassName={styles.clearIcon}
            ></Button>
          )}
          <Button
            type="button"
            className={styles.clearButton}
            onClick={handleDropdownArrowClick}
            aria-label="Clear selection"
            iconStart={isOpen ? "chevron_up" : "chevron_down"}
            iconStartClassName={classnames(styles.dropdownIcon, {
              [styles.dropdownIconDisabled]: disabled,
            })}
          ></Button>
        </div>
      </div>

      {isOpen && (
        <div
          className={classnames(styles.dropdown, {
            [styles.dropdownAbove]: dropdownPosition === "above",
            [styles.dropdownBelow]: dropdownPosition === "below",
          })}
        >
          {filteredOptions.length > 0 ? (
            <ul className={styles.optionsList}>
              {filteredOptions.map((option, index) => (
                <li
                  key={option.value}
                  className={classnames(styles.option, {
                    [styles.optionFocused]: index === focusedIndex,
                    [styles.optionSelected]: option.value === selected,
                  })}
                  onClick={() => handleOptionSelect(option.value)}
                >
                  <span className={styles.optionText}>
                    {search
                      ? highlightText(option.label, search)
                      : option.label}
                  </span>
                  {option.value === selected && (
                    <Icon name="check" className={styles.checkIcon} />
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <BodyText className={styles.noOptions}>
              No matching options found
            </BodyText>
          )}
        </div>
      )}

      {hasError && errorMessage && (
        <BodyText className={styles.errorMessage}>{errorMessage}</BodyText>
      )}
    </div>
  );
}

export { SingleSelect };
