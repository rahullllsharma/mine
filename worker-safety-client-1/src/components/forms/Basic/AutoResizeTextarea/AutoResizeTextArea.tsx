import {
  DetailedHTMLProps,
  TextareaHTMLAttributes,
  useEffect,
  useRef,
  useState,
} from "react";
import classNames from "classnames";
import styles from "./AutoResizeTextarea.module.css";

type AutoResizeTextAreaProps = DetailedHTMLProps<
  TextareaHTMLAttributes<HTMLTextAreaElement>,
  HTMLTextAreaElement
> & {
  /**
   * Add the same styles that you are applying to the textarea element to :after pseudo-element of the container
   */
  containerClassName?: string;
};

const AutoResizeTextArea = ({
  containerClassName,
  className,
  onChange,
  ...rest
}: AutoResizeTextAreaProps) => {
  const [replicatedValue, setReplicatedValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      setReplicatedValue(textareaRef.current.value);
      // Trigger onChange manually to update data-replicated-value on load
      onChangeHandler(textareaRef.current.value);
    }
  }, []);

  const onChangeHandler = (value: string) => {
    setReplicatedValue(value); // Update replicatedValue state
    onChange?.({ target: { value } } as React.ChangeEvent<HTMLTextAreaElement>);
  };

  return (
    <div
      className={classNames(
        styles.autoResizeTextAreaContainer,
        "after:w-full after:p-2 after:border-solid after:border-[1px] after:border-brand-gray-40 after:rounded",
        containerClassName
      )}
      data-replicated-value={replicatedValue} // Set the replicated value here
    >
      <textarea
        ref={textareaRef}
        className={classNames(
          styles.autoResizeTextArea,
          "w-full p-2 border-solid border-[1px] border-brand-gray-40 rounded",
          className
        )}
        onChange={e => onChangeHandler(e.target.value)}
        {...rest}
      />
    </div>
  );
};

export { AutoResizeTextArea };
