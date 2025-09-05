import type { CWFSiteConditionsProps } from "@/components/templatesComponents/customisedForm.types";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import { StaticSiteConditionCard } from "./utils";
import CWFSiteConditionComponent from "./CWFSiteConditionComponent";

const CWFSiteConditions = ({
  item,
  mode,
  section,
  activePageDetails,
  inSummary = false,
}: CWFSiteConditionsProps): JSX.Element => {
  return (
    <>
      {mode === UserFormModeTypes.BUILD ? (
        <StaticSiteConditionCard item={item} />
      ) : (
        <CWFSiteConditionComponent
          item={item}
          mode={mode}
          section={section}
          activePageDetails={activePageDetails}
          inSummary={inSummary}
        />
      )}
    </>
  );
};

export default CWFSiteConditions;
