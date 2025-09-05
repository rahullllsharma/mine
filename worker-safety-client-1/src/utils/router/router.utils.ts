import type { RouterQuery } from "@/types/Generic";

const getQueryPath = (queryName: string, queryValue: string): string => {
  const newUrl = new URL(window.location.href);
  newUrl.searchParams.set(queryName, queryValue);
  return `${newUrl.pathname}?${newUrl.searchParams}`;
};

export function pushHistoryStateQueryParam(
  queryName: string,
  queryValue: string
): void {
  const newUrl = getQueryPath(queryName, queryValue);
  history.pushState(
    { ...window.history.state, as: newUrl, url: newUrl },
    "",
    newUrl
  );
}

export function replaceHistoryStateQueryParam(
  queryName: string,
  queryValue: string
): void {
  const newUrl = getQueryPath(queryName, queryValue);
  history.replaceState(
    { ...window.history.state, as: newUrl, url: newUrl },
    "",
    newUrl
  );
}

export function getUpdatedRouterQuery(
  query: RouterQuery,
  { key, value }: { key: string; value?: string | string[] }
): RouterQuery {
  if (!value) return query;

  return { ...query, [key]: value };
}
