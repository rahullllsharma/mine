import type { LoaderParams as ListInfiniteLoaderParams } from "../loader/TableListLoader";
import type { TemplatesList } from "../customisedForm.types";
import { useIsFirstRender } from "usehooks-ts";
import { Loader as ListInfiniteLoader } from "../loader/TableListLoader";
import VersionHistoryTable from "../table/VersionHistoryTable";
import { VersionHistoryListItems } from "../listItems/VersionHistoryListItems";

type PublishedTemplatesListState = "loading" | "complete";

type PublishedTemplatesListParams = {
  listData: TemplatesList[];
  state?: PublishedTemplatesListState;
  disableFetchMore: boolean;
  onView: (id: string) => void;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function VersionHistoryList({
  listData,
  state,
  onLoadMore,
  disableFetchMore,
  onView,
}: PublishedTemplatesListParams) {
  const isFirstRender = useIsFirstRender();
  const isLoading = state === "loading";
  const isComplete = state === "complete";
  const hasInfiniteScroll = !!(onLoadMore && !isComplete && !disableFetchMore);

  return (
    <div className="overflow-y-auto max-h-56">
      {/* desktop */}
      <div className="hidden lg:flex">
        <VersionHistoryTable listData={listData} onView={onView} />
      </div>
      {/* mobile */}
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <VersionHistoryListItems listData={listData} onView={onView} />
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

export { VersionHistoryList };
export type { PublishedTemplatesListState, PublishedTemplatesListParams };
