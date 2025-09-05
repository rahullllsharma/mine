import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { useContext } from "react";

export default function useCWFFormState() {
  const { dispatch } = useContext(CustomisedFromStateContext)!;

  const setCWFFormStateDirty = (formState: boolean) => {
    dispatch({
      type: CF_REDUCER_CONSTANTS.SET_FORM_STATE,
      payload: formState,
    });
  };

  return { setCWFFormStateDirty };
}
