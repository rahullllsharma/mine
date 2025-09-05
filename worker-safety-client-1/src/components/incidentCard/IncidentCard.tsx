import cx from "classnames";
import { messages } from "@/locales/messages";

type IncidentCardProps = {
  date: string;
  title: string;
  description: string;
  severity: string;
  className?: string;
};

function IncidentCard({
  date,
  title,
  description,
  severity,
  className,
}: IncidentCardProps) {
  return (
    <div className={cx("bg-brand-gray-10 p-4", className)}>
      <div className="flex justify-between mb-4">
        <div className="font-bold">{title}</div>
        <div className="text-sm text-neutral-shade-75">{date}</div>
      </div>
      <div className="mb-4">
        <div className="font-bold text-sm mb-1">
          {messages.historicIncidentModalSeverity}
        </div>
        <div>{severity}</div>
      </div>
      <div>
        <div className="font-bold text-sm mb-1">
          {messages.historicIncidentModalDescription}
        </div>
        <div>{description}</div>
      </div>
    </div>
  );
}

export { IncidentCard };
