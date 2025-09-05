import type {
  ActivePageObjType,
  FormType,
  ProjectDetailsType,
  UserFormMode,
  WidgetType,
} from "@/components/templatesComponents/customisedForm.types";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import FormComponentWrapper from "../FormComponentWrapper";
import style from "../../createTemplateStyle.module.scss";

import { formGenerator } from "./formGenerator";

type FormRendererProps = {
  activeContents: any[];
  activePageDetails: ActivePageObjType;
  activeWidgetDetails: WidgetType;
  setActiveWidgetDetails?: (item: WidgetType) => void;
  mode: UserFormMode;
  formObject?: FormType;
  pageLevelIncludeInSummaryToggle?: boolean;
  setActivePageDetails?: (item: ActivePageObjType) => void;
  projectDetails?: ProjectDetailsType;
};

const FormRenderer = ({
  activeContents,
  activePageDetails,
  activeWidgetDetails,
  setActiveWidgetDetails,
  mode,
  formObject,
  pageLevelIncludeInSummaryToggle,
  setActivePageDetails,
  projectDetails,
}: FormRendererProps) => {
  return (
    <div className="h-full">
      <ul className={mode === UserFormModeTypes.BUILD ? style.ulContainer : ""}>
        {activeContents.map((element, index) => (
          <li key={element.id}>
            <FormComponentWrapper>
              {formGenerator(
                element,
                activePageDetails,
                activeWidgetDetails,
                mode,
                {
                  previousContent: activeContents[index - 1],
                  nextContent: activeContents[index + 1],
                },
                projectDetails,
                pageLevelIncludeInSummaryToggle,
                setActiveWidgetDetails,
                null,
                false,
                formObject,
                setActivePageDetails
              )}
            </FormComponentWrapper>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FormRenderer;
