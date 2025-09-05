import type { ReactNode } from "react";
import classnames from "classnames";

export type TagCardProps = {
  className?: string;
  withLeftBorder?: boolean;
  children: ReactNode;
  onClick?: () => void;
};

function TagCard({
  className,
  withLeftBorder = true,
  children,
  onClick,
}: TagCardProps) {
  return (
    <div
      className={classnames(
        "bg-white flex items-center shadow rounded-lg px-4 py-6",
        withLeftBorder ? "border-l-10" : "border-l-0",
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

export { TagCard };
