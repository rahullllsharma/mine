/* istanbul ignore file */
import type { ReactNode } from "react";
import type { PropsWithClassName } from "@/types/Generic";
import { fireEvent, render, screen } from "@testing-library/react";
import { FormProvider, useForm } from "react-hook-form";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { TenantMock } from "@/store/tenant/utils/tenantMock";

export const formTemplate = (
  component: ReactNode,
  defaultValues: { [key: string]: any } = {}
) => {
  function Wrapper({ children }: PropsWithClassName): JSX.Element {
    const methods = useForm({ defaultValues });
    return <FormProvider {...methods}>{children}</FormProvider>;
  }
  return <Wrapper>{component}</Wrapper>;
};

export const formRender = (
  component: ReactNode,
  defaultValues: { [key: string]: any } = {}
) => {
  return render(formTemplate(component, defaultValues));
};

// to overcome react-select limitation for testing, of not responding to click events
export const openSelectMenu = (role = "combobox", name?: RegExp): void => {
  const inputElement = screen.getByRole(role, { name });
  fireEvent.keyDown(inputElement, { key: "ArrowDown", code: "ArrowDown" });
};

export const mockTenantStore = (mock = TenantMock) => {
  const { setTenant } = useTenantStore.getState();
  setTenant(mock);
};
