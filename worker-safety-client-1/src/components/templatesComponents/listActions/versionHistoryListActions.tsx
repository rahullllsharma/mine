import type { IconName } from "@urbint/silica";
import router from "next/router";
import ButtonLarge from "@/components/shared/button/large/ButtonLarge";

type VersionHistoryListAction = {
  id: string;
  onView: (id: string) => void;
  onVersionHistory?: (id: string) => void;
};

type VersionHistoryListActionsItemProps = {
  title: string;
  icon: IconName;
  onClick: () => void;
};

function VersionHistoryListActionItem({
  title,
  icon,
  onClick,
}: VersionHistoryListActionsItemProps): JSX.Element {
  return (
    <ButtonLarge
      label={title}
      iconStart={icon}
      className="!text-left !font-normal absolute bg-white rounded shadow-20 top-7 right-0 transform translate-y-[-80%]"
      controlStateClass="!justify-start !p-4 gap-2"
      onClick={onClick}
    />
  );
}

const VersionHistoryListAction = ({
  id,
  onView,
}: VersionHistoryListAction): JSX.Element => {
  onView = () => {
    const pathname = `/templates/view`;
    const query = `templateId=${id}`;
    router.push({
      pathname,
      query,
    });
  };
  return (
    <div className="rounded bg-white min-w-[135px]">
      <div className="grid divide-y">
        <VersionHistoryListActionItem
          title="View"
          icon="show"
          onClick={() => onView(id)}
        />
      </div>
    </div>
  );
};

export default VersionHistoryListAction;
