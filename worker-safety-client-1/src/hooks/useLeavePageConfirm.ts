import useBeforeUnload from "./useBeforeUnload";

export default function useLeavePageConfirm(
  message: string,
  showPrompt: boolean
): void {
  useBeforeUnload(
    url => {
      if (showPrompt && !window.confirm(message)) {
        throw new Error(
          `Route to ${url} aborted (this error can be safely ignored)`
        );
      }
    },
    beforeUnloadEvent => {
      if (showPrompt) {
        const event = beforeUnloadEvent || window.event;
        event.returnValue = message;
        return message;
      }
    }
  );
}
