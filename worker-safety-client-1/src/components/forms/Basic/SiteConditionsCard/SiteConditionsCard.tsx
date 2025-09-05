import classnames from "classnames";

import { TagCard } from "../TagCard";

export type SiteConditionsCardProps = {
  className?: string;
  title: string;
};

function SiteConditionsCard({ className, title }: SiteConditionsCardProps) {
  return (
    <TagCard className={classnames("border-data-blue-30", className)}>
      <span className="font-semibold">{title}</span>
    </TagCard>
  );
}

export { SiteConditionsCard };
