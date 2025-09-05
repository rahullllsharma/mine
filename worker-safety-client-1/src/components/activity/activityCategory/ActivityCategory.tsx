import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import { Badge } from "@urbint/silica";
import CheckboxGroup from "@/components/checkboxGroup/CheckboxGroup";
import Accordion from "@/components/shared/accordion/Accordion";

type ActivityCategoryProps = {
  title: string;
  options: CheckboxOption[];
  value?: CheckboxOption[];
  isExpanded?: boolean;
  onItemChange: (item: CheckboxOption) => void;
  preventDuplicateIds?: boolean;
};

function ActivityCategory({
  title,
  options,
  onItemChange,
  value,
  isExpanded = false,
  preventDuplicateIds = true,
}: ActivityCategoryProps): JSX.Element {
  const count = options.length;
  return (
    <Accordion
      headerClassName="p-3 gap-2"
      isDefaultOpen={isExpanded}
      header={
        <h6 className="text-base text-neutral-shade-75 flex gap-2 items-center flex-1 justify-between">
          <span className="text-left">{title}</span>
          {!!count && <Badge label={`${count}`} />}
        </h6>
      }
    >
      <div className="px-4">
        <CheckboxGroup
          options={options}
          onItemChange={onItemChange}
          value={value}
          preventDuplicateIds={preventDuplicateIds}
        />
      </div>
    </Accordion>
  );
}

export default ActivityCategory;
