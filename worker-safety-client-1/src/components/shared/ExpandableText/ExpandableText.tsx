import type { IconName } from "@urbint/silica";
import { useState, useMemo } from "react";
import { Icon } from "@urbint/silica";
import Button from "../button/Button";

export type ExpandableTextProps = {
  description: string;
  characterLimit?: number;
  readMoreLabel?: string;
  readLessLabel?: string;
  className?: string;
  showIcon?: boolean;
  iconName?: IconName;
  iconStart?: IconName;
  iconEnd?: IconName;
};

const ExpandableText = ({
  description,
  characterLimit = 150,
  readMoreLabel = "Read more",
  readLessLabel = "Read less",
  className = "text-sm text-gray-700 leading-relaxed min-h-[80px] max-h-[200px] overflow-y-auto",
  showIcon = true,
  iconName = "chevron_big_down" as IconName,
  iconStart,
  iconEnd,
}: ExpandableTextProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Truncate description to characterLimit characters when not expanded
  const truncatedDescription = useMemo(() => {
    if (!description) return "";
    if (isExpanded) {
      return description;
    }
    return description.length > characterLimit
      ? description.substring(0, characterLimit) + "..."
      : description;
  }, [description, isExpanded, characterLimit]);

  const shouldShowToggle = description && description.length > characterLimit;

  return (
    <div className={className}>
      {truncatedDescription}
      {shouldShowToggle && (
        <Button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-brand-urbint-50 text-sm mt-2 flex items-center gap-1"
          controlStateClass={
            "hover:bg-neutral-light-16 focus:bg-transparent active:bg-transparent bg-transparent border-none"
          }
        >
          {iconStart && (
            <Icon
              name={iconStart}
              className={`text-brand-urbint-50 transition-transform ${
                isExpanded ? "rotate-180" : ""
              }`}
            />
          )}
          {isExpanded ? readLessLabel : readMoreLabel}
          {iconEnd && (
            <Icon
              name={iconEnd}
              className={`text-brand-urbint-50 transition-transform ${
                isExpanded ? "rotate-180" : ""
              }`}
            />
          )}
          {showIcon && !iconStart && !iconEnd && (
            <Icon
              className={`text-brand-urbint-50 transition-transform ${
                isExpanded ? "rotate-180" : ""
              }`}
              name={iconName}
            />
          )}
        </Button>
      )}
    </div>
  );
};

export default ExpandableText;
