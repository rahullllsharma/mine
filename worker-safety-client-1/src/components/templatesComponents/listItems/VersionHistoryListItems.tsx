import VersionHistoryCardItem from "../listCardItem/VersionHistoryCardItem";

type VersionHistoryListItemsProps = {
  listData: any;
  onView: (id: string) => void;
};
function VersionHistoryListItems({
  listData,
  onView,
}: VersionHistoryListItemsProps) {
  return (
    <>
      {listData.map((templateData: any) => (
        <VersionHistoryCardItem
          listData={templateData}
          key={templateData.id}
          onView={onView}
        />
      ))}
    </>
  );
}

export { VersionHistoryListItems };
