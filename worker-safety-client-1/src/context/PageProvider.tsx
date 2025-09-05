import type { ReactNode } from "react";
import { useContext, createContext } from "react";

type GenericProp = Record<string, unknown>;

type PageProviderProps<T extends GenericProp> = {
  children: ReactNode;
  props: T;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const PageContext = createContext<any>({});

function usePageContext<T>() {
  return useContext<T>(PageContext);
}

function PageProvider<T extends GenericProp>({
  props,
  children,
}: PageProviderProps<T>) {
  return (
    <PageContext.Provider value={{ ...props }}>{children}</PageContext.Provider>
  );
}

export { PageProvider, usePageContext };
