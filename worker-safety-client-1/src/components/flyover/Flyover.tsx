import type { PropsWithChildren, ReactNode } from "react";
import { Transition } from "@headlessui/react";
import { Fragment } from "react";
import ButtonIcon from "../shared/button/icon/ButtonIcon";

type FlyoverProps = PropsWithChildren<{
  isOpen: boolean;
  title: string;
  unmount?: boolean;
  footer?: ReactNode;
  className?: string;
  footerStyle?: string;
  onClose: () => void;
}>;

const flyOverTransitions = {
  rightToLeft: {
    enter: "transform transition ease-in-out duration-500 sm:duration-700",
    enterFrom: "translate-x-full",
    enterTo: "translate-x-0",
    leave: "transform transition ease-in-out duration-500 sm:duration-700",
    leaveFrom: "translate-x-0",
    leaveTo: "translate-x-full",
  },
};

export default function Flyover({
  isOpen,
  title,
  unmount = false,
  onClose,
  footer,
  children,
  className,
  footerStyle,
}: FlyoverProps): JSX.Element {
  const hasFooter = !!footer;

  return (
    <Transition
      {...flyOverTransitions.rightToLeft}
      unmount={unmount}
      as={Fragment}
      show={isOpen}
    >
      <aside
        className={`absolute top-0 right-0 flex flex-col gap-3 h-full w-full md:w-78 bg-white shadow-20 z-30 md:z-20 ${className}`}
        data-testid="flyover"
      >
        <header className="flex items-center justify-between bg-brand-gray-10 px-3 h-16">
          <h4 className="text-lg font-semibold text-neutral-shade-100">
            {title}
          </h4>
          <ButtonIcon iconName="close_big" onClick={onClose} />
        </header>
        <div className="flex-1 px-3 overflow-y-auto">{children}</div>
        {hasFooter && (
          <footer className={`sticky bottom-0 h-16 ${footerStyle}`}>
            {footer}
          </footer>
        )}
      </aside>
    </Transition>
  );
}
