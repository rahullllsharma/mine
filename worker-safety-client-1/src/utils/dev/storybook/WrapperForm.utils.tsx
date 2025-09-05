import type { PropsWithChildren } from "react";
import type { UseFormReturn } from "react-hook-form";
import { FormProvider, useForm } from "react-hook-form";

function WrapperForm<T = unknown>({
  children,
  // eslint-disable-next-line react-hooks/rules-of-hooks
  methods = useForm(),
}: PropsWithChildren<{ methods?: UseFormReturn<T> }>): JSX.Element {
  return <FormProvider {...methods}>{children}</FormProvider>;
}

export { WrapperForm };
