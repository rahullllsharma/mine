export type AsyncOperationStatus<T> =
  | {
      status: "Started";
    }
  | {
      status: "Finished";
      result: T;
    };

export const Started = <T>(): AsyncOperationStatus<T> => ({
  status: "Started",
});

export const Finished = <T>(result: T): AsyncOperationStatus<T> => ({
  status: "Finished",
  result,
});
