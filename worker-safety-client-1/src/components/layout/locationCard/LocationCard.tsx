import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { ReactNode } from "react";

import cx from "classnames";
import { Icon } from "@urbint/silica";
import RiskLabel from "@/components/riskLabel/RiskLabel";
import Tooltip from "../../shared/tooltip/Tooltip";

type LocationCardProps = {
  risk: RiskLevel;
  title: string;
  description?: string;
  slots?: string[];
  identifier?: ReactNode;
  isCritical?: boolean;
};

export default function LocationCard({
  risk,
  title,
  description,
  slots = [],
  identifier,
  isCritical = false,
}: LocationCardProps): JSX.Element {
  return (
    <div data-testid="location-card">
      <div className="flex justify-between">
        <Tooltip
          title={
            "The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
          }
          position="bottom"
          className="max-w-xl !left-80"
        >
          <RiskLabel risk={risk} label={`${risk}`} isCritical={isCritical} />
        </Tooltip>
        {identifier && (
          <div className="font-medium text-sm uppercase">{identifier}</div>
        )}
      </div>
      <h6 className="mt-2 text-brand-urbint-50 font-semibold text-sm">
        {title}
      </h6>
      <div className="my-2 text-neutral-shade-100 text-tiny">{description}</div>
      {slots.length > 0 && (
        <div className="text-neutral-shade-100 text-tiny">
          {slots.slice(0, 3).map((value, index) => (
            <span key={index}>
              <span className={cx({ hidden: index === 0 })}>
                <Icon name="dot_02_s" />
              </span>
              {value}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
