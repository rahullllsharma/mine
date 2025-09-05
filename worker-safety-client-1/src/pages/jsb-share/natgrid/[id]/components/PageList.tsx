import type {
  PageListItemType,
  PageListComponentType,
} from "@/utils/jsbShareUtils/jsbShare.type";
import { StepItem } from "@/components/forms/Basic/StepItem";

const PageList = ({
  listItems,
  onSelectOfPage,
  activePage,
  rawStatus
}: PageListComponentType) => {
  const getStatusOfPage = (page: PageListItemType) => {
    if(page.id === 1 || rawStatus === "COMPLETE") return "saved";
    if (activePage === page.id) {
      if (page.status === "saved") {
        return "saved_current";
      } else {
        return "current";
      }
    } else {
      return "default";
    }
  };
  return (
    <div>
      {listItems.map((page: PageListItemType) => (
        <div key={page.id} className="mb-2">
          <StepItem
            status={getStatusOfPage(page)}
            label={page.label}
            onClick={() => onSelectOfPage(page)}
          />
        </div>
      ))}
    </div>
  );
};

export default PageList;
