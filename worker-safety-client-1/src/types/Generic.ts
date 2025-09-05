import type { NextRouter } from "next/router";
import type { PropsWithChildren } from "react";

// eslint-disable-next-line @typescript-eslint/ban-types
export type PropsWithClassName<P = {}> = PropsWithChildren<
  P & { className?: string }
>;

export type RouterLink = Pick<NextRouter, "pathname" | "query">;
export type RouterQuery = Record<string, string | string[] | undefined>;
