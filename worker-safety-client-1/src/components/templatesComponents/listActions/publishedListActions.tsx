import type { IconName } from "@urbint/silica";
import ButtonLarge from "@/components/shared/button/large/ButtonLarge";

type PublishedListActionsProps = {
  id: string;
  onView: (id: string) => void;
  onVersionHistory: (templateUUID: string, templateTitle: string) => void;
  uuid: string;
  className?: string;
  templateTitle: string;
};

type PublishedListActionsItemProps = {
  title: string;
  icon: IconName;
  onClick: () => void;
};

function PublishedListActionsItem({
  title,
  icon,
  onClick,
}: PublishedListActionsItemProps): JSX.Element {
  return (
    <ButtonLarge
      label={title}
      iconStart={icon}
      className="!text-left !font-normal w-full"
      controlStateClass="!justify-start !p-4 gap-2"
      onClick={onClick}
    />
  );
}

const PublishedListAction = ({
  id,
  onView,
  onVersionHistory,
  uuid,
  className,
  templateTitle,
}: PublishedListActionsProps): JSX.Element => {
  return (
    <div className="rounded bg-white min-w-[135px]">
      <div
        className={`!text-left !font-normal absolute bg-white rounded shadow-20 top-7 w-min ${className}`}
      >
        <PublishedListActionsItem
          title="View"
          icon="edit"
          onClick={() => onView(id)}
        />
        <PublishedListActionsItem
          title="Version History"
          icon="copy"
          onClick={() => onVersionHistory(uuid, templateTitle)}
        />
      </div>
    </div>
  );
};

export default PublishedListAction;
