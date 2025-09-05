import type { ReactNode } from "react";
import type { FormFilter } from "../filters/formFilters/FormFilters";
import { noop } from "lodash-es";
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

type FormProviderProps = {
  children: ReactNode;
  defaultFilters?: FormFilter[];
};

type FormContextProps = {
  filters: FormFilter[];
  setFilters: (filters: FormFilter[]) => void;
};

//defualt filters
const defaultState: FormContextProps = {
  filters: [
    { field: "STATUS", values: [] },
    { field: "FORM", values: [] },
    { field: "WORKPACKAGE", values: [] },
    { field: "CREATEDBY", values: [] },
    { field: "CREATEDON", values: [] },
    { field: "UPDATEDBY", values: [] },
    { field: "UPDATEDON", values: [] },
    { field: "LOCATIONS", values: [] },
    { field: "COMPLETEDON", values: [] },
    { field: "REPORTDATE", values: [] },
  ],
  setFilters: noop,
};

const FormContext = createContext<FormContextProps>(defaultState);

export const useFormContext = (): FormContextProps => useContext(FormContext);

export default function FormProvider({
  children,
  defaultFilters = defaultState.filters,
}: FormProviderProps): JSX.Element {
  const [formFilters, setFormFilters] = useState(defaultFilters);
  const setFilters = useCallback((filters: FormFilter[]) => {
    setFormFilters(filters);
  }, []);

  const formContext: FormContextProps = useMemo(
    () => ({
      filters: formFilters,
      setFilters,
    }),
    [formFilters, setFilters]
  );

  return (
    <FormContext.Provider value={formContext}>{children}</FormContext.Provider>
  );
}
