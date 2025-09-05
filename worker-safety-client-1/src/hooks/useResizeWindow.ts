import { useEffect } from "react";

export default function useResizeWindow(
  minWidth: number,
  callback: (value: boolean) => void
): void {
  useEffect(() => {
    const handleResize = (e: MediaQueryListEvent) => callback(!!e.matches);

    const mql = window?.matchMedia(`(min-width: ${minWidth}px)`);
    mql.addEventListener("change", handleResize);
    callback(mql.matches);

    return () => mql.removeEventListener("change", handleResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
