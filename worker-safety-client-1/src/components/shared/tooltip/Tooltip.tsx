/* eslint-disable jsx-a11y/no-static-element-interactions */
/* eslint-disable jsx-a11y/mouse-events-have-key-events */
/* eslint-disable jsx-a11y/click-events-have-key-events */
import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import { useCallback, useRef, useState } from "react";
import { Portal, Transition } from "@headlessui/react";

export type TooltipPosition = "top" | "right" | "bottom" | "left";

export type TooltipProps = PropsWithClassName<{
  title: string;
  position?: TooltipPosition;
  isDisabled?: boolean;
  closeOnClick?: boolean;
  contentClasses?: string;
  containerClasses?: string;
}>;

export default function Tooltip({
  title,
  position = "top",
  isDisabled,
  closeOnClick,
  contentClasses = "bg-black bg-opacity-88 text-white rounded-md",
  containerClasses = "inline-flex items-center",
  className,
  children,
}: TooltipProps): JSX.Element {
  const [isOpen, setOpen] = useState(false);
  const containerRef = useRef<HTMLSpanElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);

  let positionClass;
  switch (position) {
    case "top":
      positionClass = "-translate-x-1/2 origin-bottom mb-2";
      break;
    case "bottom":
      positionClass = "-translate-x-1/2 origin-top mt-2";
      break;
    case "right":
      positionClass = "-translate-y-1/2 origin-left ml-2";
      break;
    case "left":
      positionClass = "-translate-y-1/2 origin-right mr-2";
      break;
  }

  const beforeEnter = useCallback(() => {
    const rect = containerRef.current?.getBoundingClientRect();
    const tooltip = tooltipRef.current;

    if (rect && tooltip) {
      switch (position) {
        case "top":
          tooltip.style.bottom = `${window.innerHeight - rect.top}px`;
          tooltip.style.left = `${rect.left + rect.width / 2}px`;
          break;
        case "bottom":
          tooltip.style.top = `${rect.bottom}px`;
          tooltip.style.left = `${rect.left + rect.width / 2}px`;
          break;
        case "right":
          tooltip.style.left = `${rect.left + rect.width}px`;
          tooltip.style.top = `${rect.top + rect.height / 2}px`;
          break;
        case "left":
          tooltip.style.right = `${window.innerWidth - rect.left}px`;
          tooltip.style.top = `${rect.top + rect.height / 2}px`;
          break;
      }
    }
  }, [position]);

  const tooltipClickHandler = () => {
    if (closeOnClick) {
      setOpen(false);
    }
  };

  return (
    <>
      <span
        className={containerClasses}
        onMouseOver={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={tooltipClickHandler}
        ref={containerRef}
      >
        <span className="inline-flex items-center w-full">{children}</span>
      </span>
      {title && (
        <Portal>
          <div ref={tooltipRef} className={cx("absolute z-50", className)}>
            <Transition
              as="div"
              className={cx(
                positionClass,
                "shadow-xl px-3 py-1.5 text-tiny text-center transition transform-gpu duration-100 scale-0",
                contentClasses
              )}
              data-position={position}
              appear
              show={isOpen && !isDisabled}
              enterFrom="scale-0 opacity-0"
              enterTo="scale-full opacity-100"
              beforeEnter={beforeEnter}
              leaveFrom="scale-full opacity-100"
              leaveTo="scale-0 opacity-0"
            >
              {title}
            </Transition>
          </div>
        </Portal>
      )}
    </>
  );
}
