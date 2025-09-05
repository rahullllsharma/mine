import type { PropsWithClassName } from "@/types/Generic";
import type { ReactNode } from "react";
import cx from "classnames";
import { Popover as HeadlessUiPopover, Transition } from "@headlessui/react";
import { Fragment } from "react";

export type PopoverProps = PropsWithClassName<{
  triggerComponent: ReactNode;
}>;

export default function Popover({
  triggerComponent,
  className,
  children,
}: PopoverProps): JSX.Element {
  return (
    <HeadlessUiPopover className="relative">
      <HeadlessUiPopover.Button as={Fragment}>
        {triggerComponent}
      </HeadlessUiPopover.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-200"
        enterFrom="opacity-0 translate-y-1"
        enterTo="opacity-100 translate-y-0"
        leave="transition ease-in duration-150"
        leaveFrom="opacity-100 translate-y-0"
        leaveTo="opacity-0 translate-y-1"
      >
        <HeadlessUiPopover.Panel
          className={cx("absolute z-10 mt-2", className)}
        >
          <div className="w-full h-full bg-white rounded shadow-20">
            {children}
          </div>
        </HeadlessUiPopover.Panel>
      </Transition>
    </HeadlessUiPopover>
  );
}
