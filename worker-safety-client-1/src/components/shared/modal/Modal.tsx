import type { PropsWithClassName } from "@/types/Generic";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import cx from "classnames";
import ButtonIcon from "../button/icon/ButtonIcon";

export type ModalSize = "sm" | "md" | "lg" | "xl";

export type ModalProps = PropsWithClassName<{
  title: string;
  subtitle?: string;
  isOpen: boolean;
  size?: ModalSize;
  closeModal: () => void;
  dismissable?: boolean;
}>;

export default function Modal({
  title,
  children,
  className,
  isOpen,
  size = "md",
  subtitle,
  closeModal,
  dismissable = false,
}: ModalProps): JSX.Element {
  const modalWidth = cx("mx-2 w-full sm:mx-0", {
    ["sm:max-w-[300px] sm:w-auto"]: size === "sm",
    ["sm:max-w-[500px]"]: size === "md",
    ["sm:max-w-[500px] md:max-w-[700px] lg:max-w-[900px]"]:
      size === "lg" || size === "xl",
    ["xl:max-w-[1200px] 2xl:max-w-[1400px]"]: size === "xl",
  });

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog
        as="div"
        className="fixed inset-0 z-10 overflow-y-auto bg-neutral-shade-26"
        static={dismissable}
        onClose={dismissable ? () => null : closeModal}
      >
        <div className="min-h-screen flex items-center justify-center">
          <Dialog.Overlay className="fixed inset-0 cursor-pointer" />

          {/* This element is to trick the browser into centering the modal contents. */}
          <span
            className="inline-block h-screen align-middle"
            aria-hidden="true"
          >
            &#8203;
          </span>

          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-120"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <div
              className={cx(
                "flex flex-col text-left p-6 transition-all transform bg-white shadow-30 rounded-lg",
                modalWidth,
                className
              )}
            >
              <Dialog.Title
                as="div"
                className="flex items-center text-neutral-shade-100 font-semibold"
              >
                <header className="flex-1">
                  <h6>{title}</h6>
                  {subtitle && (
                    <span className="font-normal text-sm text-neutral-shade-75">
                      {subtitle}
                    </span>
                  )}
                </header>
                <ButtonIcon
                  iconName="close_big"
                  className="leading-5"
                  onClick={closeModal}
                  title="Close modal"
                />
              </Dialog.Title>

              <Dialog.Description
                as="div"
                className="flex flex-col flex-1 justify-center text-base text-neutral-shade-100 mt-4"
              >
                {children}
              </Dialog.Description>
            </div>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
