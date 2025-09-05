import type { TemplatesList } from "../customisedForm.types";
import { useRouter } from "next/router";
import DraftListCardItem from "../listCardItem/DraftListCardItem";

type PublishedTemplatesListItemsProps = {
  listData: TemplatesList[];
  isLoading?: boolean;
  onEdit: (id: string) => void;
  onPublishTemplate: (id: string) => void;
};

function DraftTemplatesListItems({
  listData,
  onEdit,
  onPublishTemplate,
}: PublishedTemplatesListItemsProps) {
  const router = useRouter();
  const templateNavigator = (templateList: TemplatesList) => {
    const pathname = `/templates/create`;
    const query = `templateId=${templateList.id}`;
    router.push({
      pathname,
      query,
    });
  };

  return (
    <>
      {listData.map((templateData: TemplatesList) => (
        <DraftListCardItem
          listData={templateData}
          key={templateData.id}
          onClick={() => templateNavigator(templateData)}
          onEdit={onEdit}
          onPublishTemplate={onPublishTemplate}
        />
      ))}
    </>
  );
}

export { DraftTemplatesListItems };
