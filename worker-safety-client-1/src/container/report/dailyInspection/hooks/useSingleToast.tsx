import type { ToastType } from "@/components/shared/toast/toastItem/Toast";

import type { ToastItem } from "@/components/shared/toast/context/ToastContext";
import { useContext } from "react";
import ToastContext from "@/components/shared/toast/context/ToastContext";

type ReplaceActiveToast = (type: ToastType, message: string) => void;

/**
 * Only display one toast at each time.
 *
 * @description
 * Pop the last toast and replace with a new one.
 *
 * @returns [(type: ToastType, message: string) => void]
 *
 * @deprecated DO NOT USE THIS, will be removed
 */
const useSingleToast = (): [ReplaceActiveToast] => {
  let lastActiveToast: ToastItem;
  const toastCtx = useContext(ToastContext);

  const replaceActiveToast: ReplaceActiveToast = (type, message) => {
    if (!lastActiveToast) {
      [lastActiveToast] = toastCtx?.items || [];
    }

    if (toastCtx?.items.some(item => item.id === lastActiveToast?.id)) {
      toastCtx?.dismissToast(lastActiveToast.id);
    }

    toastCtx?.pushToast(type, message);
    [lastActiveToast] = toastCtx?.items || [];
  };

  return [replaceActiveToast];
};

export default useSingleToast;
