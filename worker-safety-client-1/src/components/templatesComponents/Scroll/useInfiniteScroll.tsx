import { useEffect, useRef } from "react";

export function useInfiniteScroll(
  loadMore: () => void,
  isFetching: boolean,
  hasNextPage: boolean
) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (isFetching || !hasNextPage) return;

    const onIntersect: IntersectionObserverCallback = ([entry]) => {
      if (entry.isIntersecting) loadMore();
    };

    const observer = new IntersectionObserver(onIntersect, {
      rootMargin: "200px 0px",
      threshold: 0,
    });

    sentinelRef.current && observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [loadMore, isFetching, hasNextPage]);

  return sentinelRef;
}
