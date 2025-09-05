import type { ToastType } from "../toastItem/Toast";
import React from "react";

export type ToastContextProps = {
  items: ToastItem[];
  pushToast: (type: ToastType, message: string) => void;
  dismissToast: (id: string) => void;
};

export type ToastItem = {
  id: string;
  message: string;
  type: ToastType;
};

export default React.createContext<ToastContextProps | null>(null);
