import type {
  FormComponentPayloadType,
  FormElementsType,
  PageType,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText } from "@urbint/silica";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import { Toggle } from "@/components/forms/Basic/Toggle";

type IncludeInSummaryToggleProps = {
  includeSectionInSummaryToggle: boolean;
  handleToggle?: (() => void) | false;
  mode?: UserFormMode;
  item?: PageType | FormElementsType | FormComponentPayloadType;
};

const IncludeInSummaryToggle = ({
  includeSectionInSummaryToggle,
  handleToggle,
  mode,
  item,
}: IncludeInSummaryToggleProps): JSX.Element => {
  const showDivider = () => {
    if (mode === UserFormModeTypes.PREVIEW_PROPS) {
      if (
        item &&
        item?.type !== CWFItemType.Attachment &&
        item?.type !== CWFItemType.HazardsAndControls &&
        item?.type !== CWFItemType.ActivitiesAndTasks &&
        item?.type !== CWFItemType.SiteConditions &&
        item?.type !== CWFItemType.Location &&
        item?.type !== CWFItemType.NearestHospital &&
        item?.type !== CWFItemType.Section
      ) {
        return true;
      }
    }
    if (mode === UserFormModeTypes.BUILD) {
      return true;
    }
    return false;
  };

  return (
    <>
      <div className="flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div
            className={`flex items-center py-1 border-borders ${
              showDivider() ? "pl-3 border-l-2" : ""
            }`}
          >
            <BodyText>Include in Summary</BodyText>
          </div>
          <div className="flex items-center justify-center pt-2">
            <Toggle
              checked={includeSectionInSummaryToggle}
              onClick={() => {
                if (handleToggle) {
                  handleToggle();
                }
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default IncludeInSummaryToggle;
