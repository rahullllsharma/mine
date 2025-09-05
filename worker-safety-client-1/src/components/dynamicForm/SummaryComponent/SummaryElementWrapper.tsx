import type { ActivePageObjType } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, Icon } from "@urbint/silica";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import Button from "@/components/shared/button/Button";

type SummaryElementWrapperProps = {
  elementId: string;
  pageMap?: Record<string, string>;
  setActivePageDetails?: (details: ActivePageObjType) => void;
  activePageDetails?: ActivePageObjType;
  isFormFullySaved?: boolean;
};

const SummaryElementWrapper = ({
  elementId,
  pageMap,
  setActivePageDetails,
  activePageDetails,
  isFormFullySaved,
}: SummaryElementWrapperProps) => {
  const { formObject } = useFormRendererContext();
  const handleEdit = () => {
    const parentPageId = pageMap?.[elementId];
    if (parentPageId && activePageDetails && setActivePageDetails) {
      setActivePageDetails({
        id: parentPageId,
        parentId: "root",
        type: CWFItemType.Page,
        returnToSummaryPage: true,
        summaryPageId: activePageDetails.id,
      });
    }
  };
  return (
    <>
      {formObject?.type === "form" && !isFormFullySaved && (
        <div className="flex items-end w-full flex-col">
          <Button
            className="flex flex-col font-semibold items-center text-base border border-borders rounded-md px-3"
            labelClassName={"flex items-center font-semibold"}
            onClick={handleEdit}
          >
            <Icon name="edit" className="text-xl pr-2" />
            <BodyText className="text-base font-semibold">Edit</BodyText>
          </Button>
        </div>
      )}
    </>
  );
};

export default SummaryElementWrapper;
