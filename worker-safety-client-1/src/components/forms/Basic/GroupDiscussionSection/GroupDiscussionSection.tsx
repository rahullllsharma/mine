import { SectionHeading, Icon } from "@urbint/silica";
import { FieldGroup } from "@/components/shared/FieldGroup";

type GroupDiscussionSectionProps = {
  title: string;
  onClickEdit?: () => void;
};

const GroupDiscussionSection: React.FC<GroupDiscussionSectionProps> = ({
  title,
  onClickEdit,
  children,
}) => {
  return (
    <FieldGroup>
      <div className="flex justify-between">
        <SectionHeading className="text-lg font-semibold text-neutral-shade-75">
          {title}
        </SectionHeading>

        {onClickEdit && (
          <button
            onClick={onClickEdit}
            className="text-brand-urbint-50 flex items-center"
          >
            <Icon name="edit" />
            <span className="ml-1">Edit</span>
          </button>
        )}
      </div>

      <div className="mt-4">{children}</div>
    </FieldGroup>
  );
};

export { GroupDiscussionSection };
