import type { ToastItem } from "./context/ToastContext";
import React, { useContext, useEffect, useState } from "react";
import { Transition } from "@headlessui/react";
import ToastContext from "./context/ToastContext";
import Toast from "./toastItem/Toast";

const ToastContent = ({ id, type, message }: ToastItem): JSX.Element => {
  const timeoutDelay = 4000;
  const ctx = useContext(ToastContext);
  const [isShowing, setIsShowing] = useState(true);

  useEffect(() => {
    const timeout = setTimeout(() => dismissToastHandler(), timeoutDelay);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const dismissToastHandler = (): void => setIsShowing(false);

  return (
    <div className="mb-2 last:mb-0">
      <Transition
        appear
        show={isShowing}
        enter="transition-opacity duration-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
        leave="transition-opacity duration-300"
        leaveFrom="opacity-100"
        leaveTo="opacity-0"
        afterLeave={() => ctx?.dismissToast(id)}
      >
        <Toast type={type} message={message} onDismiss={dismissToastHandler} />
      </Transition>
    </div>
  );
};

export default function ToastManager(): JSX.Element {
  const ctx = useContext(ToastContext);

  return (
    <div className="fixed top-16 w-fit px-4 left-2/4 -translate-x-1/2 z-50 flex flex-col items-center">
      {ctx?.items.map((toast: ToastItem) => (
        <ToastContent key={toast.id} {...toast} />
      ))}
    </div>
  );
}
