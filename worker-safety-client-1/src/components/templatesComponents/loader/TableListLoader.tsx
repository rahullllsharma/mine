import { useRef, useLayoutEffect, useCallback } from "react";
import { TableLoader } from "@/components/table/loader/TableLoader";

type LoaderParams = {
  isLoading: boolean;
  shouldLoadMore: boolean;
  onLoadMore: () => void;
};

function Loader({ isLoading, onLoadMore, shouldLoadMore }: LoaderParams) {
  const ref = useRef<HTMLDivElement | null>(null);
  const lastLoadTimeRef = useRef(0);
  const minLoadInterval = 1000;

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      for (const e of entries) {
        if (e.isIntersecting && !isLoading && shouldLoadMore) {
          const now = Date.now();
          if (now - lastLoadTimeRef.current >= minLoadInterval) {
            lastLoadTimeRef.current = now;
            onLoadMore?.();
          }
        }
      }
    },
    [isLoading, onLoadMore, shouldLoadMore]
  );

  useLayoutEffect(() => {
    if (!ref?.current || !shouldLoadMore) {
      return;
    }

    const observer = new IntersectionObserver(handleIntersection, {
      rootMargin: "100px",
      threshold: 0.1,
    });

    observer.observe(ref.current);
    return () => {
      observer.disconnect();
    };
  }, [handleIntersection, shouldLoadMore]);

  return (
    <div ref={ref} className="py-4 lg:bg-white" data-testid="list-form-loader">
      <div className="hidden lg:block">
        <TableLoader columnsSize={4} rows={3} />
      </div>
    </div>
  );
}

export { Loader };
export type { LoaderParams };
