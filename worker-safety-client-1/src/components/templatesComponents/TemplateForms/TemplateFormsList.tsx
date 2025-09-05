import type { LoaderParams as ListInfiniteLoaderParams } from "../loader/TableListLoader";
import { useIsFirstRender } from "usehooks-ts";
import { Loader as ListInfiniteLoader } from "../loader/TableListLoader";
import TemplateFormCardView from "./CardView/TemplateFormCardView";
import TemplateFormTable from "./TableView/TemplateFormTable";

type PublishedTemplatesListState = "loading" | "complete";

type TemplateFormsListParams = {
  templateFormsData: any[];
  state?: PublishedTemplatesListState;

  disableFetchMore: boolean;
  onView: (id: string) => void;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function TemplateFormsList({
  templateFormsData,
  state,
  onLoadMore,
  disableFetchMore,
  onView,
}: TemplateFormsListParams) {
  const isFirstRender = useIsFirstRender();

  const isLoading = state === "loading";
  const isComplete = state === "complete";
  const hasInfiniteScroll = onLoadMore && !isComplete && !disableFetchMore;

  return (
    <div className="overflow-y-auto">
      {/* desktop */}
      <div className="hidden lg:flex">
        <TemplateFormTable
          templateFormsData={templateFormsData}
          isLoading={isLoading}
        />
      </div>
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card">
        {templateFormsData.map(data => (
          <TemplateFormCardView
            templateFormsData={data}
            key={data.id}
            isLoading={isLoading}
            onView={onView}
          />
        ))}
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

export { TemplateFormsList };
