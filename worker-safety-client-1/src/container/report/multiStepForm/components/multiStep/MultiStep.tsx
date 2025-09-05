import type { MultiStepFormProps } from "../../MultiStepForm";

import type { FormEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { useForm, useFormContext, FormProvider } from "react-hook-form";

import { DevTool } from "@hookform/devtools";

import { noop } from "lodash-es";
import cx from "classnames";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import { scrollToFirstErrorSection } from "@/components/shared/field/utils/field.utils";
import MultiStepNavigation from "../multiStepNavigation/MultiStepNavigation";
import {
  useMultiStepActions,
  useMultiStepState,
} from "../../hooks/useMultiStep";

type OnFormSubmitHandler<T = Element> = (event?: FormEvent<T>) => void;

function MultiStep({
  readOnly = false,
  onStepMount,
  onStepUnmount,
  onStepSave,
  onComplete,
  UNSAFE_WILL_BE_REMOVED_debugMode = false,
}: Omit<MultiStepFormProps, "steps">): JSX.Element {
  const methods = useFormContext();

  const stepContent = useRef<HTMLDivElement>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { areAllStepsCompleted, current, steps } = useMultiStepState();
  const { moveForward, moveBack, markCurrentAs } = useMultiStepActions();

  const [isFormCompleteAndPristine, setIsFormCompletedAndPristine] =
    useState(areAllStepsCompleted);

  const primaryActionLabel = isSubmitting
    ? "Saving..."
    : `Save and ${isFormCompleteAndPristine ? "complete" : "continue"}`;

  useEffect(() => {
    return () => {
      const formData = methods.getValues() ?? {};
      onStepUnmount?.({
        [current.id]: formData[current.id],
      });

      // We need this due the the sections not using RHF state
      methods.reset(
        {
          [current.id]: {},
        },
        {
          keepDirty: false,
          keepDefaultValues: false,
        }
      );
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current.id]);

  useEffect(() => {
    // scroll top on of step on step change if there is no errors on the form
    if (Object.keys(methods.formState.errors).length === 0) {
      stepContent.current?.scrollTo(0, 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [steps]);

  useEffect(() => {
    if (
      methods.formState.isSubmitted &&
      Object.values(methods.formState.errors).length > 0
    ) {
      markCurrentAs("error");
      scrollToFirstErrorSection();
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [methods.formState.isSubmitted, methods.formState.errors]);

  useEffect(() => {
    if (!isSubmitting) {
      const values = methods.getValues();
      methods.reset(values, {
        keepValues: true,
        keepDirty: false,
        keepErrors: true,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSubmitting]);

  useEffect(() => {
    if (!areAllStepsCompleted) {
      if (isFormCompleteAndPristine) {
        setIsFormCompletedAndPristine(false);
      }
      return;
    }

    // After the last section is successfully submitted
    if (
      methods.formState.isSubmitted &&
      methods.formState.isSubmitSuccessful &&
      !isFormCompleteAndPristine
    ) {
      const values = methods.getValues();
      methods.reset(values);
      setIsFormCompletedAndPristine(true);
      return;
    }

    if (methods.formState.isDirty && isFormCompleteAndPristine) {
      // After a pristine report is changed
      setIsFormCompletedAndPristine(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    methods.formState.isDirty,
    methods.formState.isSubmitSuccessful,
    areAllStepsCompleted,
  ]);

  /**
   * After the form is submitted sucessefully, we can safely move to the next section
   * This way, we can use RHF to skip displaying the confirm dialog (see useDispatchWithEvents on the useMultiStep)
   *
   * BEWARE: this could (potentially) trigger on other events that submit the form.
   */
  useEffect(() => {
    if (methods.formState.isSubmitSuccessful) {
      markCurrentAs("completed");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [methods.formState.isSubmitSuccessful]);

  /**
   * Handle the submission for the form.
   *
   * Due to partial updates, we need to ALWAYS store the section to backend, but we still
   * need to track the validation status to so we mark the section as completed or not.
   *
   * @returns
   */
  const onFormSubmitHandler: OnFormSubmitHandler = async () => {
    setIsSubmitting(true);
    const sectionIsValid = await methods.trigger(undefined, {
      shouldFocus: true,
    });

    // We call the handleSubmit programmatically to trigger the proper formStates including the
    // submittion information back so we don't have to change the logic for completing a report.
    methods
      .handleSubmit(noop)()
      .finally(async () => {
        await onStepSave?.({
          [current.id]: {
            ...methods.getValues(current.id),
          },
          sectionIsValid,
        });
        setIsSubmitting(false);
      });
  };

  const onPrimaryBtnClickHandler = () => {
    if (isFormCompleteAndPristine) {
      return onComplete?.(methods.getValues());
    }

    return onFormSubmitHandler();
  };

  return (
    <form
      onSubmit={onFormSubmitHandler}
      className="grid gap-4 grid-rows-2-auto-expand md:grid-rows-none md:grid-cols-2-auto-expand h-full w-screen responsive-padding-x overflow-hidden pb-12"
    >
      <aside
        data-testid="multi-step-navigation"
        data-multi-step-form-nav="true"
        className="bg-white justify-self-start w-full max-w-[240px] md:overflow-y-scroll
          md:col-span-1 md:py-6 md:px-3 md:justify-self-stretch
          md:max-w-xs md:min-w-max md:w-[33vw]"
      >
        <MultiStepNavigation />
      </aside>
      <section className="flex flex-col gap-4 bg-white pt-6 md:pt-6 sm:pt-0 md:pb-14 overflow-auto">
        <div className="h-full overflow-y-scroll px-6" ref={stepContent}>
          <current.Component {...onStepMount?.()} />
        </div>
        {/* skip this in tests */}
        {typeof window !== "undefined" &&
          window?.__NEXT_DATA__?.buildId === "development" &&
          UNSAFE_WILL_BE_REMOVED_debugMode && (
            <div className="flex flex-col col-span-2">
              <DevTool control={methods.control} placement="top-left" />
              <div className="flex justify-between">
                <button type="button" onClick={() => markCurrentAs("default")}>
                  change to DEFAULT
                </button>
                <button
                  type="button"
                  onClick={() => markCurrentAs("completed")}
                >
                  change to COMPLETED
                </button>
                <button type="button" onClick={() => markCurrentAs("error")}>
                  change to ERROR
                </button>
              </div>
              <div className="flex justify-between">
                <button type="button" onClick={() => moveBack()}>
                  back
                </button>
                <button type="button" onClick={() => moveForward()}>
                  next
                </button>
              </div>
            </div>
          )}
        {!readOnly && (
          <PageFooter
            primaryActionLabel={primaryActionLabel}
            isPrimaryActionLoading={isSubmitting}
            className={cx("absolute left-0 right-0 bottom-0")}
            onPrimaryClick={onPrimaryBtnClickHandler}
          />
        )}
      </section>
    </form>
  );
}

/**
 * This component is needed to wrap the form context around the MultiStep
 * This way, we can continue to use useFormContext and useMultiStepContext without having to pass any argument around.
 *
 * @param {Omit<MultiStepFormProps, "steps">} props
 * @returns {JSX.Element}
 */
export default function MultiStepWithForm(
  props: Omit<MultiStepFormProps, "steps">
): JSX.Element {
  const { current } = useMultiStepState();
  const { form = {}, ...onStepMountProps } = props.onStepMount?.() || {};

  const methods = useForm({
    mode: "onBlur",
    reValidateMode: "onChange",
    shouldUnregister: false,
  });

  useLeavePageConfirm(
    "Discard unsaved changes?",
    methods.formState.isDirty && !methods.formState.isSubmitted
  );

  // https://stackoverflow.com/questions/62242657/how-to-change-react-hook-form-defaultvalue-with-useeffect#answer-63343527
  useEffect(() => {
    if (form?.[current.id]) {
      methods.reset(
        {
          [current.id]: form[current.id],
        },
        {
          keepDirty: false,
          keepDefaultValues: false,
        }
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current.id]);

  return (
    <FormProvider {...methods}>
      <MultiStep {...props} onStepMount={() => onStepMountProps} />
    </FormProvider>
  );
}
