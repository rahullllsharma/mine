import type {
  PersonnelComponentType,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import PersonnelComponentTemplatePlaceholder from "./PersonnelComponentTemplatePlaceholder";
import PersonnelComponentForm from "./PersonnelComponentForm";
import { RenderPersonnelComponentInSummary } from "./RenderPersonnelComponentInSummary";

const PersonnelComponent = ({
  item,
  mode,
  inSummary,
}: {
  item: PersonnelComponentType;
  mode: UserFormMode;
  inSummary?: boolean;
}) => {
  if (inSummary) {
    return (
      <RenderPersonnelComponentInSummary
        item={item as PersonnelComponentType}
      />
    );
  }
  return mode === UserFormModeTypes.PREVIEW_PROPS ||
    mode === UserFormModeTypes.BUILD ? (
    <PersonnelComponentTemplatePlaceholder
      isDisabled={true}
      properties={item.properties}
    />
  ) : (
    <PersonnelComponentForm item={item} mode={mode} inSummary={inSummary} />
  );
};

export default PersonnelComponent;
