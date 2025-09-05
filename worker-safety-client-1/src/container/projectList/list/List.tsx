import type { Project } from "@/types/project/Project";
import type { LoaderParams as ListInfiniteLoaderParams } from "./components/loader/Loader";
import { useIsFirstRender } from "usehooks-ts";
import ProjectTable from "@/container/table/ProjectTable";
import { ProjectItems } from "./components/projectItems/ProjectItems";
import { Loader as ListInfiniteLoader } from "./components/loader/Loader";

type ListState = "loading" | "complete";

type ListParams = {
  projects: Project[];
  state?: ListState;
} & Partial<Pick<ListInfiniteLoaderParams, "onLoadMore">>;

function List({ projects, state, onLoadMore }: ListParams) {
  const isFirstRender = useIsFirstRender();
  const isLoading = state === "loading";
  const isComplete = state === "complete";

  const hasInfiniteScroll = !!(onLoadMore && !isComplete);

  return (
    <div className="overflow-y-auto">
      {/* desktop */}
      <div className="hidden lg:flex">
        <ProjectTable projects={projects} />
      </div>
      {/* mobile */}
      <div className="lg:hidden grid gap-4 grid-cols-auto-fill-list-card pb-16">
        <ProjectItems projects={projects} />
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
