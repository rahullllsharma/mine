import type { Form } from "@/types/formsList/formsList";
import { useRef, useLayoutEffect } from "react";
import { TableLoader } from "@/components/table/loader/TableLoader";
import FormCardItem from "@/components/cardItem/FormCardItem";

type LoaderParams = {
  isLoading: boolean;
  shouldLoadMore: boolean;
  onLoadMore: () => void;
};
const formData: Form = {
  id: "",
  status: "",
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
    <div ref={ref} className="py-4 lg:bg-white" data-testid="list-form-loader">
      <div className="hidden lg:block">
        <TableLoader columnsSize={6} rows={3} />
      </div>
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <FormCardItem formsData={formData} isLoading />
        <FormCardItem formsData={formData} isLoading />
      </div>
    </div>
  );
}

export { Loader };
export type { LoaderParams };
