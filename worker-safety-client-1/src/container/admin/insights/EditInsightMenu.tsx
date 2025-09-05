import type { IconName } from "@urbint/silica";
import ButtonLarge from "@/components/shared/button/large/ButtonLarge";

interface EditInsightMenuProps {
  id: string;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

type EditInsightMenuItemProps = {
  title: string;
  icon: IconName;
  onClick: () => void;
};

function EditInsightMenuItem({
  title,
  icon,
  onClick,
}: EditInsightMenuItemProps): JSX.Element {
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

const EditInsightMenu = ({
  id,
  onEdit,
  onDelete,
}: EditInsightMenuProps): JSX.Element => {
  return (
    <div className="rounded bg-white min-w-[135px]">
      <div className="grid divide-y">
        <EditInsightMenuItem
          title="Edit"
          icon="edit"
          onClick={() => onEdit(id)}
        />
        <EditInsightMenuItem
          title="Delete"
          icon="trash_empty"
          onClick={() => onDelete(id)}
        />
      </div>
    </div>
  );
};

export default EditInsightMenu;
