import type { ReactNode } from "react";

function WrapperScroll({ children }: { children: ReactNode }): JSX.Element {
  return <div className="p-2 overflow-y-scroll h-screen">{children}</div>;
}

export { WrapperScroll };
