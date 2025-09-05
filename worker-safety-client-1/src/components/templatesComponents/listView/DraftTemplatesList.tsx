import type { LoaderParams as ListInfiniteLoaderParams } from "../loader/TableListLoader";
import type { TemplatesList } from "../customisedForm.types";
import { useIsFirstRender } from "usehooks-ts";
import { Loader as ListInfiniteLoader } from "../loader/TableListLoader";
import DraftTemplatesTable from "../table/DraftTemplatesTable";
import { DraftTemplatesListItems } from "../listItems/DraftTemplatesListItems";

type DraftTemplatesListState = "loading" | "complete";

type DraftTemplatesListParams = {
  listData: TemplatesList[];
  state?: DraftTemplatesListState;
  disableFetchMore: boolean;
  onPublishTemplate: (id: string) => void;
  onEdit: (id: string) => void;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function DraftTemplatesList({
  listData,
  state,
  onLoadMore,
  disableFetchMore,
  onPublishTemplate,
  onEdit,
}: DraftTemplatesListParams) {
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
        <DraftTemplatesTable
          listData={listData}
          onEdit={onEdit}
          onPublishTemplate={onPublishTemplate}
        />
      </div>
      {/* mobile */}
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        <DraftTemplatesListItems
          listData={listData}
          onEdit={onEdit}
          onPublishTemplate={onPublishTemplate}
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

export { DraftTemplatesList };
export type { DraftTemplatesListState, DraftTemplatesListParams };
