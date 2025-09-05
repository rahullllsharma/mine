import type { PropsWithChildren } from "react";
import { SectionHeading, Subheading } from "@urbint/silica";
import { FieldGroup } from "@/components/shared/FieldGroup";
import Button from "@/components/shared/button/Button";

export type SummarySectionWrapperOnClickEdit = {
  onClickEdit: () => void;
};

type SummarySectionWrapperProps = SummarySectionWrapperOnClickEdit & {
  title: string;
  isSectionContentCollapsed?: boolean;
  onSectionContentCollapse?: () => void;
  isEmpty: boolean;
  isEmptyText?: string;
  isReadOnly: boolean;
  subtitle?: string;
};

function SummarySectionWrapper({
  title,
  onClickEdit,
  subtitle,
  isSectionContentCollapsed = false,
  onSectionContentCollapse,
  isEmpty,
  isEmptyText = "No data was entered for this section.",
  children,
  isReadOnly,
}: PropsWithChildren<SummarySectionWrapperProps>) {
  return (
    <FieldGroup>
      <div className="flex justify-start items-center gap-4">
        <SectionHeading className="text-lg font-semibold text-neutral-shade-75">
          {title}
        </SectionHeading>
        <div className="flex flex-row justify-end gap-4 ml-auto">
          {onSectionContentCollapse && (
            <Button
              onClick={onSectionContentCollapse}
              className="text-brand-urbint-50 flex items-center gap-1"
              label={isSectionContentCollapsed ? "Expand all" : "Collapse all"}
              iconStart={
                isSectionContentCollapsed
                  ? "chevron_duo_down"
                  : "chevron_duo_up"
              }
            />
          )}
          {onClickEdit && !isReadOnly && (
            <Button
              onClick={onClickEdit}
              className="text-brand-urbint-50 flex items-center gap-1"
              label="edit"
              iconStart="edit"
            />
          )}
        </div>
      </div>
      {subtitle && (
        <Subheading className="text-lg font-semibold text-neutral-shade-75">
          {subtitle}
        </Subheading>
      )}
      <div>{isEmpty ? <span>{isEmptyText}</span> : children}</div>
    </FieldGroup>
  );
}

export default SummarySectionWrapper;
