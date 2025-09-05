import type {
  SubPageContentType,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";

type SectionProperties = {
  title: string;
  is_repeatable?: boolean;
  sectionContents: SubPageContentType[];
  mode: UserFormMode;
};

const RepeatableSection = ({
  title,
  is_repeatable,
  sectionContents,
  mode,
}: SectionProperties) => {
  const addRepeatedSectionToForm = () => {
    console.log("Test", sectionContents);
    // Logic to add a repeated section to the form
    // This could involve updating the state or context that manages the form sections
    // For example, you might want to push a new section into an array of sections
    // setSections((prevSections) => [...prevSections, newSection]);
    // Or if you're using a context provider, you might call a function from the context to add the section
    // dispatch({ type: "ADD_SECTION", payload: newSection });
    // You can also use a modal or a toast notification to inform the user that the section has been added
    // Example:
    // toast.success("Section added successfully!");
  };
  return is_repeatable ? (
    <div className="flex flex-col gap-2 justify-end items-end mt-2 mb-2">
      <ButtonSecondary
        onClick={addRepeatedSectionToForm}
        label={"Add another " + title}
        iconStart="plus_circle_outline"
        disabled={
          mode === UserFormModeTypes.BUILD ||
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
        }
      />
    </div>
  ) : null;
};

export default RepeatableSection;
