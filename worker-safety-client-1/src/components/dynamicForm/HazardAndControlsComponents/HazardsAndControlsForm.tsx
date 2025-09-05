import type { HazardControl } from "../../templatesComponents/customisedForm.types";
import { UserFormModeTypes } from "../../templatesComponents/customisedForm.types";
import { HazardsBlankField } from "./utils";
import EnergyAndHazards from "./EnergyAndHazards";

type HazardsAndControlsFormProps = {
  mode?: string;
  formData: HazardControl | undefined;
  subTitle: string;
  inSummary?: boolean;
};

const HazardsAndControlsForm = ({
  mode,
  formData,
  subTitle,
  inSummary = false,
}: HazardsAndControlsFormProps) => {
  // Determine if we're in summary view based on mode
  const isPreviewMode =
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS;
  return (
    <>
      {mode === UserFormModeTypes.BUILD ? (
        <HazardsBlankField />
      ) : (
        <EnergyAndHazards
          readOnly={isPreviewMode}
          preSelectedHazards={formData}
          isSummaryView={inSummary} // Pass flag to indicate summary/preview view
          subTitle={subTitle}
        />
      )}
    </>
  );
};

export default HazardsAndControlsForm;
