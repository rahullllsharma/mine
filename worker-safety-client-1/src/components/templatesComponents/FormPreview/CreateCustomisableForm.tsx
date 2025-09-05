import type {
  FormType,
  LinkComponentObj,
  ProjectDetailsType,
  UserFormMode,
  WorkPackageData,
} from "../customisedForm.types";
import CustomisedFormStateProvider from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import FormPreview from ".";

type CustomisableFormPreviewProps = {
  formObject: FormType;
  mode: UserFormMode;
  linkObj: LinkComponentObj;
  workPackageData?: WorkPackageData;
  setMode?: (mode: UserFormMode) => void;
  projectDetails?: ProjectDetailsType;
  creatingForm?: boolean;
};
const CreateCustomisableForm = ({
  formObject,
  mode,
  linkObj,
  workPackageData,
  setMode,
  projectDetails,
  creatingForm,
}: CustomisableFormPreviewProps) => {
  return (
    <div className="flex flex-col bg-brand-gray-10   h-[100dvh]  w-full">
      <CustomisedFormStateProvider>
        <FormPreview
          setMode={setMode}
          formObject={formObject}
          mode={mode}
          linkObj={linkObj}
          workPackageData={workPackageData}
          projectDetails={projectDetails}
          creatingForm={creatingForm}
        />
      </CustomisedFormStateProvider>
    </div>
  );
};

export default CreateCustomisableForm;
