import type { FormHeaderProps } from "../../customisedForm.types";
import router from "next/router";
import { ProjectDescriptionHeader } from "@/container/projectSummaryView/PojectDescriptionHeader/ProjectDescriptionHeader";
import LinkComponent from "../../LinkComponent";
import { UserFormModeTypes } from "../../customisedForm.types";
import FormHeading from "./FormHeading";

export default function TemplateFormHeader({
  mode,
  linkObj,
  workPackageData,
  formObject,
  setMode,
}: FormHeaderProps) {
  const description = formObject.properties?.description || "";

  return (
    <header className="bg-white pl-6 pr-6 pt-2 flex items-center">
      <div className="flex flex-col w-full">
        {mode === UserFormModeTypes.PREVIEW &&
        router.pathname.includes("/templates/") ? null : (
          <LinkComponent href={linkObj.linkHref} labelName={linkObj.linkName} />
        )}
        <FormHeading
          workPackageData={workPackageData}
          formObject={formObject}
          setMode={setMode}
        />
        <div className="mt-2">
          <ProjectDescriptionHeader
            description={description}
            maxCharacters={100}
          />
        </div>
      </div>
    </header>
  );
}
