import type { ReactNode } from "react";
import type { ToastType } from "../toastItem/Toast";
import type { ToastContextProps, ToastItem } from "./ToastContext";
import { nanoid } from "nanoid";
import { useState } from "react";
import ToastManager from "../ToastManager";
import ToastContext from "./ToastContext";

type ToastProviderProps = {
  children: ReactNode;
};

export default function ToastProvider({
  children,
}: ToastProviderProps): JSX.Element {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const isPushToastAllowed = toasts.length < 5;

  const pushToastHandler = (type: ToastType, message: string): void => {
    if (isPushToastAllowed) {
      //closing previous toast from list before display new one
      if (toasts.length > 0) {
        dismissToastHandler(toasts[0].id);
      }

      const toast = {
        id: nanoid(),
        type,
        message,
      };
      //To avoid overflowing the screen with notifications
      setToasts(prevState => [...prevState, toast]);
    }
  };

  const dismissToastHandler = (id: string): void =>
    setToasts(prevState => prevState.filter(toast => toast.id !== id));

  const toastContext: ToastContextProps = {
    items: toasts,
    pushToast: pushToastHandler,
    dismissToast: dismissToastHandler,
  };

  return (
    <ToastContext.Provider value={toastContext}>
      {children}
      <ToastManager />
    </ToastContext.Provider>
  );
}
