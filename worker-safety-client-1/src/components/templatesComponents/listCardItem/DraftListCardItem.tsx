import type { HTMLAttributes } from "react";
import type { TemplatesList } from "../customisedForm.types";
import { useRouter } from "next/router";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import DraftListAction from "../listActions/draftListActions";
import CardRow from "./cardRow/CardRow";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  listData: TemplatesList;
  isLoading?: boolean;
  onEdit: (id: string) => void;
  onPublishTemplate: (id: string) => void;
};

function CardItemContent({
  listData,
  onEdit,
  onPublishTemplate,
}: CardItemProps): JSX.Element {
  // const { formList } = useTenantStore(state => state.getAllEntities());
  const router = useRouter();
  const templateNavigator = () => {
    const pathname = `/templates/create`;
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
        <PopoverIcon iconName="more_horizontal" className="right-0">
          <DraftListAction
            id={listData.id}
            onEdit={onEdit}
            onPublishTemplate={onPublishTemplate}
          />
        </PopoverIcon>
      </header>
      <div className="mt-4">
        <CardRow label="Last Updated By">
          {listData?.updated_by?.user_name}
        </CardRow>
      </div>
      <div className="mt-4">
        <CardRow label="Last Updated On">{listData?.updated_at}</CardRow>
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
  onEdit,
  onPublishTemplate,
}: CardItemProps): JSX.Element {
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        <div className="flex-1 p-6 text-left">
          <CardItemContent
            listData={listData}
            onEdit={onEdit}
            onPublishTemplate={onPublishTemplate}
          />
        </div>
      )}
    </div>
  );
}
