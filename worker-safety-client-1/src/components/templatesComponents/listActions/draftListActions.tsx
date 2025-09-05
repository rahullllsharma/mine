import type { IconName } from "@urbint/silica";
import ButtonLarge from "@/components/shared/button/large/ButtonLarge";

type DraftListActionsProps = {
  id: string;
  onPublishTemplate: (id: string) => void;
  onEdit: (id: string) => void;
};

type DraftListActionsItemProps = {
  title: string;
  icon: IconName;
  onClick: () => void;
};

function DraftListActionsItem({
  title,
  icon,
  onClick,
}: DraftListActionsItemProps): JSX.Element {
  return (
    <ButtonLarge
      label={title}
      iconStart={icon}
      className="!text-left !font-normal"
      controlStateClass="!justify-start !p-4 gap-2"
      onClick={onClick}
    />
  );
}

const DraftListAction = ({
  id,
  onPublishTemplate,
  onEdit,
}: DraftListActionsProps): JSX.Element => {
  return (
    <div className="rounded bg-white min-w-[135px]">
      <div className="grid divide-y">
        <DraftListActionsItem
          title="Edit"
          icon="edit"
          onClick={() => onEdit(id)}
        />
        <DraftListActionsItem
          title="Publish"
          icon="cloud_up"
          onClick={() => onPublishTemplate(id)}
        />
      </div>
    </div>
  );
};

export default DraftListAction;
