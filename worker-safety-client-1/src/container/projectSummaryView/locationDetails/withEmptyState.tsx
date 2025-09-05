import type { ComponentType } from "react";

export type WithEmptyStateProps<T, Y = T> = {
  elements: T[];
  onElementClick: (element: Y) => void;
};

export type ConfigType = {
  Empty: ComponentType;
  Container: ComponentType;
};

export function withEmptyState<P, T extends WithEmptyStateProps<P, Y>, Y = P>(
  Component: ComponentType<T>,
  config: ConfigType
): (props: T) => JSX.Element {
  const { Empty, Container } = config;

  return function WrappedComponent(props: T) {
    const isEmpty = props.elements.length === 0;

    return (
      <Container>{isEmpty ? <Empty /> : <Component {...props} />}</Container>
    );
  };
}
