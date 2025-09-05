import type {
  ActivePageObjType,
  FormType,
  ProjectDetailsType,
  UserFormMode,
} from "../../customisedForm.types";
import { BodyText } from "@urbint/silica";
import FormRenderer from "../../CreateTemplateLayout/PreviewComponent/FormRenderer";

const FormWidgetSection = ({
  activeContents,
  activePageDetails,
  mode,
  formObject,
  setActivePageDetails,
  projectDetails,
}: {
  activeContents: any;
  activePageDetails: ActivePageObjType;
  mode: UserFormMode;
  formObject: FormType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  projectDetails?: ProjectDetailsType;
}) => {
  return (
    <div>
      {activeContents.length === 0 ? (
        <div className="p-2">
          <BodyText>No Content is added yet</BodyText>
        </div>
      ) : (
        <FormRenderer
          activeContents={activeContents}
          activePageDetails={activePageDetails}
          activeWidgetDetails={null}
          mode={mode}
          formObject={formObject}
          setActivePageDetails={setActivePageDetails}
          projectDetails={projectDetails}
        />
      )}
    </div>
  );
};

export default FormWidgetSection;
