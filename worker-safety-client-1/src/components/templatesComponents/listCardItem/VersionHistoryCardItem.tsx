/* istanbul ignore file */
import type { HTMLAttributes } from "react";
import type { TemplatesList } from "../customisedForm.types";
import { useRouter } from "next/router";
import { DateTime } from "luxon";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import VersionHistoryListAction from "../listActions/versionHistoryListActions";
import CardRow from "./cardRow/CardRow";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  listData: TemplatesList;
  isLoading?: boolean;
  onView: (id: string) => void;
};

function CardItemContent({ listData, onView }: CardItemProps): JSX.Element {
  // const { formList } = useTenantStore(state => state.getAllEntities());
  const router = useRouter();
  const versionHistoryNavigator = () => {
    const pathname = `/templates/view`;
    const query = `templateId=${listData?.template_unique_id}`;
    router.push({
      pathname,
      query,
    });
  };

  onView = () => {
    const pathname = `/templates/view`;
    const query = `templateId=${listData?.id}`;
    router.push({
      pathname,
      query,
    });
  };
  return (
    <>
      <header className="text-neutral-shade-100 text-lg font-semibold flex items-center">
        <button
          className="flex-1 p-6 text-left pl-0"
          onClick={() => versionHistoryNavigator()}
        >
          {listData?.title}
        </button>
        <div className="w-full flex relative justify-end">
          <PopoverIcon
            iconName="more_horizontal"
            className="right-0 absolute bottom-8 mt-0"
          >
            <VersionHistoryListAction id={listData?.id} onView={onView} />
          </PopoverIcon>
        </div>
      </header>
      <div className="mt-4">
        <CardRow label={"Version"}>{listData.version}</CardRow>
      </div>
      <div className="mt-4">
        <CardRow label={"Published By"}>
          {listData.published_by?.user_name}
        </CardRow>
      </div>
      <div className="mt-4">
        <CardRow label={"Published On"}>
          {listData?.published_at
            ? DateTime.fromISO(listData?.published_at).toFormat("MM-dd-yyyy")
            : ""}
        </CardRow>
      </div>
    </>
  );
}

function CardItemPlaceholder(): JSX.Element {
  const itemRowPlaceholder = (
    <div className="flex border-solid border-t my-1 py-1 text-sm ">
      <span className="flex-1">
        <div className="h-3 rounded animate-pulse w-1/3 bg-gray-300"></div>
      </span>
      <span className="h-3 rounded animate-pulse w-2/5 bg-gray-200"></span>
    </div>
  );
  return (
    <div className="flex-1 p-6">
      <header className="h-5 rounded animate-pulse w-1/2 bg-gray-300" />
      <div className="mt-4">
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
      </div>
    </div>
  );
}

export default function VersionHistoryCardItem({
  listData,
  isLoading,
  // onClick,
  onView,
}: CardItemProps): JSX.Element {
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        // <button className="flex-1 p-6 text-left" onClick={onClick}>
        <div className="flex-1 p-6 text-left">
          <CardItemContent listData={listData} onView={onView} />
        </div>
        // </button>
      )}
    </div>
  );
}
