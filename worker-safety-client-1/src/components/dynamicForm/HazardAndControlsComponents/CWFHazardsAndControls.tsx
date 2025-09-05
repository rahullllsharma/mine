import type {
  ActivePageObjType,
  HazardsAndControlsFormType,
} from "../../templatesComponents/customisedForm.types";
import { FormProvider, useForm } from "react-hook-form";
import { useContext } from "react";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import HazardsAndControlsComponent from "./HazardsAndControlsComponent";

const CWFHazardsAndControls = ({
  mode,
  item,
  inSummary,
}: {
  mode: string;
  section: any;
  activePageDetails: ActivePageObjType;
  item: HazardsAndControlsFormType;
  inSummary?: boolean;
}) => {
  const { state } = useContext(CustomisedFromStateContext)!;

  // Get hazards and controls data from form state
  const hazardsControlsData = state.form.component_data?.hazards_controls;

  const methods = useForm({
    defaultValues: {
      hazards_controls: hazardsControlsData,
    },
  });

  return (
    <FormProvider {...methods}>
      <HazardsAndControlsComponent
        configs={{
          title: item.properties.title || "Hazards And Controls",
          buttonIcon: "image_alt",
          subTitle: item.properties.sub_title,
        }}
        mode={mode}
        formData={hazardsControlsData}
        inSummary={inSummary}
      />
    </FormProvider>
  );
};

export default CWFHazardsAndControls;
