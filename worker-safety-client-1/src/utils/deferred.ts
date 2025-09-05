import type { Option } from "fp-ts/lib/Option";
import { none, some } from "fp-ts/lib/Option";

export type Deferred<T> =
  | {
      status: "NotStarted";
    }
  | {
      status: "InProgress";
    }
  | {
      status: "Updating";
      value: T;
    }
  | {
      status: "Resolved";
      value: T;
    };

export const NotStarted = <T>(): Deferred<T> => ({
  status: "NotStarted",
});

export const InProgress = <T>(): Deferred<T> => ({
  status: "InProgress",
});

export const Updating = <T>(value: T): Deferred<T> => ({
  status: "Updating",
  value,
});

export const Resolved = <T>(value: T): Deferred<T> => ({
  status: "Resolved",
  value,
});

export const mapDeferred =
  <T, R>(fn: (_: T) => R) =>
  (deferred: Deferred<T>): Deferred<R> => {
    switch (deferred.status) {
      case "NotStarted":
        return { status: "NotStarted" };
      case "InProgress":
        return { status: "InProgress" };
      case "Updating":
        return { status: "Updating", value: fn(deferred.value) };
      case "Resolved":
        return { status: "Resolved", value: fn(deferred.value) };
    }
  };

export const updatingDeferred = <T>(deferred: Deferred<T>): Deferred<T> => {
  switch (deferred.status) {
    case "NotStarted":
    case "InProgress":
      return { status: "InProgress" };
    case "Updating":
    case "Resolved":
      return { status: "Updating", value: deferred.value };
  }
};

export const isResolved = <T>(
  deferred: Deferred<T>
): deferred is { status: "Resolved"; value: T } =>
  deferred.status === "Resolved";

export const isUpdating = <T>(
  deferred: Deferred<T>
): deferred is { status: "Updating"; value: T } =>
  deferred.status === "Updating";

export const isInProgress = <T>(
  deferred: Deferred<T>
): deferred is { status: "InProgress"; value: T } =>
  deferred.status === "InProgress";

export const deferredToOption = <T>(deferred: Deferred<T>): Option<T> => {
  switch (deferred.status) {
    case "NotStarted":
    case "InProgress":
      return none;
    case "Updating":
    case "Resolved":
      return some(deferred.value);
  }
};
