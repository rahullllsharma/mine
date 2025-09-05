import type { ReactNode } from "react";

export type DialogSize = "flex" | "small" | "medium" | "large";

export type DialogProps = {
  size?: DialogSize;
  header?: JSX.Element;
  footer?: JSX.Element;
  children: ReactNode;
};

function contentSizeClass(size?: DialogSize): string {
  switch (size) {
    case "flex":
      return "";
    case "small":
      return "w-[20rem] h-[20rem]";
    case "medium":
      return "max-w-[100dvw] max-h-[90dvh] md:w-[30rem] md:h-[40rem]";
    case "large":
      return "w-screen-lg h-screen-lg";
    default:
      return "max-w-screen-sm max-h-[80vh]";
  }
}

export function Dialog({
  size,
  header,
  footer,
  children,
}: DialogProps): JSX.Element {
  return (
    <div className="fixed z-20 inset-0 bg-black bg-opacity-50 flex w-screen h-screen justify-center items-center">
      <div
        className={`flex flex-col bg-white shadow rounded-lg p-4 py-6 md:p-6 ${contentSizeClass(
          size
        )}`}
      >
        {header && <div className="mb-6 flex-shrink-0">{header}</div>}
        <div className="flex-1 overflow-auto">{children}</div>
        {footer && <div className="mt-6 flex-shrink-0">{footer}</div>}
      </div>
    </div>
  );
}
