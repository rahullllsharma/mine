import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useContext } from "react";
import ButtonPrimary from "../button/primary/ButtonPrimary";
import ToastContext from "./context/ToastContext";
import ToastProvider from "./context/ToastProvider";

import ToastManager from "./ToastManager";

export default {
  title: "Silica/Toast",
  component: ToastManager,
  argTypes: { onDismiss: { action: "onDismiss" } },
} as ComponentMeta<typeof ToastManager>;

const ChildrenComponent = () => {
  const ctx = useContext(ToastContext);

  return (
    <div className="flex flex-col items-start">
      <ButtonPrimary
        label="Send error"
        className="mb-2"
        onClick={() => ctx?.pushToast("error", "Something went wrong")}
      />
      <ButtonPrimary
        label="Send warning"
        className="mb-2"
        onClick={() => ctx?.pushToast("warning", "Attention!")}
      />
      <ButtonPrimary
        label="Send success"
        className="mb-2"
        onClick={() => ctx?.pushToast("success", "Operation successful")}
      />
      <ButtonPrimary
        label="Send info"
        onClick={() => ctx?.pushToast("info", "Sending some information")}
      />
    </div>
  );
};

const Template: ComponentStory<typeof ToastManager> = () => {
  return (
    <ToastProvider>
      <ChildrenComponent />
    </ToastProvider>
  );
};

export const Playground = Template.bind({});
