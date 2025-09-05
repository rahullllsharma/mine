import type { Project } from "@/types/project/Project";
import { useRef, useLayoutEffect } from "react";
import CardItem from "@/components/cardItem/CardItem";
import { TableLoader } from "@/components/table/loader/TableLoader";

type LoaderParams = {
  isLoading: boolean;
  shouldLoadMore: boolean;
  onLoadMore: () => void;
};

function Loader({ isLoading, onLoadMore, shouldLoadMore }: LoaderParams) {
  const ref = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    if (!ref?.current || !shouldLoadMore) {
      return;
    }

    const observer = new IntersectionObserver(entries => {
      for (const e of entries) {
        if (e.isIntersecting && !isLoading) {
          onLoadMore?.();
        }
      }
    }, {});

    observer.observe(ref.current);
    return () => {
      observer.disconnect();
    };
  }, [isLoading, onLoadMore, shouldLoadMore]);

  return (
    <div
      ref={ref}
      className="py-4 lg:bg-white"
      data-testid="list-project-loader"
    >
      <div className="hidden lg:block">
        <TableLoader columnsSize={6} rows={3} />
      </div>
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <CardItem project={{} as unknown as Project} isLoading />
        <CardItem project={{} as unknown as Project} isLoading />
      </div>
    </div>
  );
}

export { Loader };
export type { LoaderParams };
