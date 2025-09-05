import type { LoaderParams as ListInfiniteLoaderParams } from "./components/loader/Loader";
import type { Form } from "../../../types/formsList/formsList";
import { useIsFirstRender } from "usehooks-ts";
import FormsTable from "../../table/FormsTable";
import { Loader as ListInfiniteLoader } from "./components/loader/Loader";
import { FormItems } from "./components/formItems/FormItems";

type ListState = "loading" | "complete";

type ListParams = {
  formsData: Form[];
  state?: ListState;
  disableFetchMore: boolean;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function List({ formsData, state, onLoadMore, disableFetchMore }: ListParams) {
  const isFirstRender = useIsFirstRender();
  const isLoading = state === "loading";
  const isComplete = state === "complete";
  const hasInfiniteScroll = !!(onLoadMore && !isComplete && !disableFetchMore);

  return (
    <div className="overflow-y-auto">
      {/* desktop */}
      <div className="hidden lg:flex">
        <FormsTable formsData={formsData} />
      </div>
      {/* mobile */}
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <FormItems formsData={formsData} />
      </div>
      {/* Include infinite scroll support */}
      {hasInfiniteScroll && (
        <ListInfiniteLoader
          onLoadMore={onLoadMore}
          isLoading={isLoading}
          shouldLoadMore={!isFirstRender}
        />
      )}
    </div>
  );
}

export { List };
export type { ListState, ListParams };
