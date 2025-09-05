import type { ReactNode } from "react";
import { noop } from "lodash-es";
import { useContext, createContext } from "react";

type ProjectSummaryContext = {
  refetchActivitiesBasedOnLocation: () => void;
};

type ProjectSummaryViewProviderProps = ProjectSummaryContext & {
  children: ReactNode;
};

const ProjectSummaryViewContext = createContext<ProjectSummaryContext>({
  refetchActivitiesBasedOnLocation: noop,
});

const useProjectSummaryEvents = () => useContext(ProjectSummaryViewContext);

const ProjectSummaryViewProvider = ({
  children,
  refetchActivitiesBasedOnLocation,
}: ProjectSummaryViewProviderProps) => {
  const context = {
    refetchActivitiesBasedOnLocation,
  };

  return (
    <ProjectSummaryViewContext.Provider value={context}>
      {children}
    </ProjectSummaryViewContext.Provider>
  );
};

export type { ProjectSummaryContext };
export {
  ProjectSummaryViewContext,
  ProjectSummaryViewProvider,
  useProjectSummaryEvents,
};
