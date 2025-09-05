/* istanbul ignore file */
import type { HTMLAttributes } from "react";
import type { TemplatesList } from "../customisedForm.types";
import { useRouter } from "next/router";
import { DateTime } from "luxon";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import PublishedListAction from "../listActions/publishedListActions";
import CardRow from "./cardRow/CardRow";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  listData: TemplatesList;
  isLoading?: boolean;
  onView: (id: string) => void;
  onVersionHistory: (id: string, templateTitle: string) => void;
};

function CardItemContent({
  listData,
  onView,
  onVersionHistory,
}: CardItemProps): JSX.Element {
  // const { formList } = useTenantStore(state => state.getAllEntities());
  const router = useRouter();
  const templateNavigator = () => {
    const pathname = `/templates/view`;
    const query = `templateId=${listData.id}`;
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
          onClick={() => templateNavigator()}
        >
          {listData?.title}
        </button>
        <PopoverIcon
          iconName="more_horizontal"
          className="right-0 absolute bottom-8 mt-0"
        >
          <PublishedListAction
            id={listData?.id || ""}
            onView={onView}
            onVersionHistory={onVersionHistory}
            uuid={listData?.template_unique_id}
            className={"right-0"}
            templateTitle={listData?.title || ""}
          />
        </PopoverIcon>
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

export default function PublishedListCardItem({
  listData,
  isLoading,
  // onClick,
  onView,
  onVersionHistory,
}: CardItemProps): JSX.Element {
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        <div className="flex-1 p-6 text-left">
          <CardItemContent
            listData={listData}
            onView={onView}
            onVersionHistory={onVersionHistory}
          />
        </div>
      )}
    </div>
  );
}
