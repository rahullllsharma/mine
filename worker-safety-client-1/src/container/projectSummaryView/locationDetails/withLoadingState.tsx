import type { ComponentType } from "react";
import type { ConfigType, WithEmptyStateProps } from "./withEmptyState";

export type WithLoadingStateProps<T, Y = T> = WithEmptyStateProps<T, Y> & {
  isLoading: boolean;
};

type LoadingConfigType = ConfigType & {
  Loading: ComponentType;
};

export function withLoadingState<
  P,
  T extends WithLoadingStateProps<P, Y>,
  Y = P
>(
  Component: ComponentType<T>,
  config: LoadingConfigType
): (props: T) => JSX.Element {
  const { Empty, Container, Loading } = config;

  return function WrappedComponent(props: T) {
    const isEmpty = props.elements.length === 0;
    const isLoading = props.isLoading;

    return (
      <Container>
        {isLoading && <Loading />}
        {isEmpty && !isLoading && <Empty />}
        {!isEmpty && !isLoading && <Component {...props} />}
      </Container>
    );
  };
}
