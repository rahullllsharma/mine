import type { ReactNode } from "react";
import { Icon } from "@urbint/silica";
import { Disclosure, Transition } from "@headlessui/react";
import cx from "classnames";

/**
 * Collection of available panel transitions.
 *
 */
const panelTransitions = {
  pop: {
    enter: "transition duration-200 ease-out",
    enterFrom: "transform scale-95 opacity-0",
    enterTo: "transform scale-100 opacity-100",
    leave: "transition duration-75 ease-out",
    leaveFrom: "transform scale-100 opacity-100",
    leaveTo: "transform scale-95 opacity-0",
  },
} as const;

export interface AccordionProps {
  header: ReactNode;
  headerClassName?: string;
  children: ReactNode;
  isDefaultOpen?: boolean;
  animation?: "none" | keyof typeof panelTransitions;
  unmount?: boolean;
  forceOpen?: boolean;
}

export default function Accordion({
  header,
  children,
  headerClassName = "",
  isDefaultOpen = false,
  animation = "none",
  unmount = true,
  forceOpen = false,
}: AccordionProps): JSX.Element {
  const panelTransitionProps =
    animation === "none" ? {} : panelTransitions[animation];

  return (
    <Disclosure defaultOpen={isDefaultOpen}>
      {({ open }) => (
        <>
          <Disclosure.Button
            className={cx(
              "flex justify-between items-center w-full",
              headerClassName
            )}
          >
            {header}
            <Icon
              name="chevron_big_down"
              // TODO: until we have a "size", we need to manually set the size of this icon.
              // We cannot use `text-xl` because that utility class sets both the font-size as well as the line-height
              className={cx("text-[1.375rem] leading-0", {
                "transform transition ease-in-out duration-200":
                  animation !== "none",
                "rotate-0": open,
                "rotate-180": !open,
              })}
            />
          </Disclosure.Button>
          <Transition
            unmount={unmount}
            show={open || forceOpen}
            {...panelTransitionProps}
          >
            <Disclosure.Panel unmount={unmount}>{children}</Disclosure.Panel>
          </Transition>
        </>
      )}
    </Disclosure>
  );
}
