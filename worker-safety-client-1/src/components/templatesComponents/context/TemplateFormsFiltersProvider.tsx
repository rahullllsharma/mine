import type { ReactNode } from "react";

import type { TemplateFormsFilter } from "../filter/TemplateFormFilters";
import { noop } from "lodash-es";
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

type TemplateFormsFiltersProviderProps = {
  children: ReactNode;
  defaultFilters?: TemplateFormsFilter[];
};

type TemplateFormsContextProps = {
  filters: TemplateFormsFilter[];
  setFilters: (filters: TemplateFormsFilter[]) => void;
};

//default filters

const defaultState: TemplateFormsContextProps = {
  filters: [
    { field: "FORMNAME", values: [] },
    { field: "STATUS", values: [] },
    { field: "CREATEDBY", values: [] },
    { field: "CREATEDON", values: [] },
    { field: "UPDATEDBY", values: [] },
    { field: "UPDATEDON", values: [] },
    { field: "COMPLETEDON", values: [] },
    { field: "LOCATION", values: [] },
    { field: "WORKPACKAGE", values: [] },
    { field: "REGION", values: [] },
    { field: "REPORTEDON", values: [] },
    { field: "SUPERVISOR", values: [] },
  ],
  setFilters: noop,
};

const TemplateFormsFilterContext =
  createContext<TemplateFormsContextProps>(defaultState);

export const useTemplateFormsFilterContext = (): TemplateFormsContextProps =>
  useContext(TemplateFormsFilterContext);

export default function FormProvider({
  children,
  defaultFilters = defaultState.filters,
}: TemplateFormsFiltersProviderProps): JSX.Element {
  const [publishedFilters, setPublishedFilters] = useState(defaultFilters);
  const setFilters = useCallback((filters: TemplateFormsFilter[]) => {
    setPublishedFilters(filters);
  }, []);

  const formContext: TemplateFormsContextProps = useMemo(
    () => ({
      filters: publishedFilters,
      setFilters,
    }),
    [publishedFilters, setFilters]
  );

  return (
    <TemplateFormsFilterContext.Provider value={formContext}>
      {children}
    </TemplateFormsFilterContext.Provider>
  );
}
