import type { ReactNode } from "react";
import type { PropsWithClassName } from "@/types/Generic";

export type TaskCardProps = PropsWithClassName<{
  isOpen?: boolean;
  taskHeader: ReactNode;
}>;

export default function TaskCard({
  isOpen = true,
  taskHeader,
  className,
  children,
}: TaskCardProps): JSX.Element {
  return (
    <div
      className={`bg-white shadow-10 rounded-lg mb-2.5 border-l-8 whitespace-break-spaces ${className}`}
      data-testid="taskCard"
    >
      <header className="flex justify-between items-center">
        {taskHeader}
      </header>

      {children && isOpen && <div className={`p-4`}>{children}</div>}
    </div>
  );
}
