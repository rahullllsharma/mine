// CommonStateContext.tsx
import type {
  CommonAction,
  FormBuilderModeProps,
  FormType,
} from "@/components/templatesComponents/customisedForm.types";
import type { Dispatch } from "react";
import { createContext, useContext, useCallback, useMemo } from "react";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";

export interface CustomisedFromContextStateType {
  form: FormType;
  formBuilderMode: FormBuilderModeProps;
  isFormDirty: boolean;
  isFormIsValid: boolean;
}

interface CommonContextProps {
  state: CustomisedFromContextStateType;
  dispatch: Dispatch<CommonAction>;
}

const CustomisedFromStateContext = createContext<CommonContextProps | null>(
  null
);

// Widget count hook that uses the form context
export const useWidgetCount = () => {
  const context = useContext(CustomisedFromStateContext);
  if (context === null) {
    throw new Error(
      "useWidgetCount must be used within a CustomisedFormStateProvider"
    );
  }

  const { state, dispatch } = context;

  const widgetCount = state.form.settings?.widgets_added || 0;
  const maxWidgetCount = state.form.settings?.maximum_widgets || 15;

  const incrementWidgetCount = useCallback(() => {
    dispatch({
      type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
      payload: {
        widgets_added: Math.min(widgetCount + 1, maxWidgetCount),
      },
    });
  }, [dispatch, widgetCount, maxWidgetCount]);

  const decrementWidgetCount = useCallback(() => {
    dispatch({
      type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
      payload: {
        widgets_added: Math.max(widgetCount - 1, 0),
      },
    });
  }, [dispatch, widgetCount]);

  const setWidgetCountDirectly = useCallback(
    (count: number) => {
      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
        payload: {
          widgets_added: Math.max(0, Math.min(count, maxWidgetCount)),
        },
      });
    },
    [dispatch, maxWidgetCount]
  );

  const canAddWidget = widgetCount < maxWidgetCount;

  return useMemo(
    () => ({
      widgetCount,
      maxWidgetCount,
      incrementWidgetCount,
      decrementWidgetCount,
      setWidgetCountDirectly,
      canAddWidget,
    }),
    [
      widgetCount,
      maxWidgetCount,
      incrementWidgetCount,
      decrementWidgetCount,
      setWidgetCountDirectly,
      canAddWidget,
    ]
  );
};

export default CustomisedFromStateContext;
