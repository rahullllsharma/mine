import type { LoaderParams as ListInfiniteLoaderParams } from "../loader/TableListLoader";
import type { TemplatesList } from "../customisedForm.types";
import { useIsFirstRender } from "usehooks-ts";
import PublishedTemplatesTable from "../table/PublishedTemplatesTable";
import { Loader as ListInfiniteLoader } from "../loader/TableListLoader";
import { PublishedTemplatesListItems } from "../listItems/PublishedTemplatesListItems";

type PublishedTemplatesListState = "loading" | "complete";

type PublishedTemplatesListParams = {
  listData: TemplatesList[];
  state?: PublishedTemplatesListState;
  disableFetchMore: boolean;
  onView: (id: string) => void;
  onVersionHistory: (id: string, templateTitle: string) => void;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function PublishedTemplatesList({
  listData,
  state,
  onLoadMore,
  disableFetchMore,
  onView,
  onVersionHistory,
}: PublishedTemplatesListParams) {
  const isFirstRender = useIsFirstRender();
  const isLoading = state === "loading";
  const isComplete = state === "complete";
  const hasInfiniteScroll = !!(
    onLoadMore &&
    !isComplete &&
    !disableFetchMore &&
    !isLoading
  );

  return (
    <div className="overflow-y-auto">
      {/* desktop */}
      <div className="hidden lg:flex">
        <PublishedTemplatesTable
          listData={listData}
          onView={onView}
          onVersionHistory={onVersionHistory}
        />
      </div>
      {/* mobile */}
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <PublishedTemplatesListItems
          listData={listData}
          onView={onView}
          onVersionHistory={onVersionHistory}
        />
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

export { PublishedTemplatesList };
export type { PublishedTemplatesListState, PublishedTemplatesListParams };
