import type { FormComponentsFooterType } from "../customisedForm.types";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";


const FormsComponentsPopUpFooter = ({addButtonHandler,cancelButtonHandler,isDisabled}:FormComponentsFooterType) => {
    return  <div className="flex w-full pt-4 m-t-4 border-t-2 border-solid mt-4 flex-wrap justify-end gap-x-2 gap-y-2">
    <ButtonSecondary
      label={"Cancel"}
      onClick={cancelButtonHandler}
    />
    <ButtonPrimary
      disabled={isDisabled}
      label={"Add"}
      onClick={addButtonHandler}
    />
</div>
}

export default FormsComponentsPopUpFooter