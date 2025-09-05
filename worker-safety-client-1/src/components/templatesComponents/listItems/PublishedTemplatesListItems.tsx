import type { TemplatesList } from "../customisedForm.types";
import { useRouter } from "next/router";
import PublishedListCardItem from "../listCardItem/PublishedListCardItem";

type PublishedTemplatesListItemsProps = {
  listData: any;
  isLoading?: boolean;
  onView: (id: string) => void;
  onVersionHistory: (id: string, templateTitle: string) => void;
};

function PublishedTemplatesListItems({
  listData,
  onView,
  onVersionHistory,
}: PublishedTemplatesListItemsProps) {
  const router = useRouter();
  const templateNavigator = (templateList: TemplatesList) => {
    const pathname = `/${templateList.title}`;
    router.push({
      pathname,
    });
  };

  return (
    <>
      {listData.map((templateData: TemplatesList) => (
        <PublishedListCardItem
          listData={templateData}
          key={templateData?.id}
          onClick={() => templateNavigator(templateData)}
          onView={onView}
          onVersionHistory={onVersionHistory}
        />
      ))}
    </>
  );
}

export { PublishedTemplatesListItems };
