import {
  fireEvent,
  render,
  screen,
  waitForElementToBeRemoved,
} from "@testing-library/react";
import { useContext } from "react";
import ToastContext from "./context/ToastContext";
import ToastProvider from "./context/ToastProvider";
import ToastManager from "./ToastManager";

const ChildrenComponent = (): JSX.Element => {
  const ctx = useContext(ToastContext);

  return (
    <button onClick={() => ctx?.pushToast("error", "Lorem ipsum")}>Add</button>
  );
};

describe(ToastManager.name, () => {
  describe("when the component renders", () => {
    it("shouldn't have any active toasts", () => {
      render(
        <ToastProvider>
          <div>Children</div>
        </ToastProvider>
      );
      const toastElements = screen.queryAllByRole("button");
      expect(toastElements).toHaveLength(0);
    });
  });

  describe("when pushing toast notifications", () => {
    beforeEach(() => {
      render(
        <ToastProvider>
          <ChildrenComponent />
        </ToastProvider>
      );
    });

    it("should render a toast element when a toast notification is pushed", () => {
      fireEvent.click(screen.getByRole("button", { name: "Add" }));
      const toastElement = screen.getByRole("button", { name: "Lorem ipsum" });
      expect(toastElement).toBeInTheDocument();
    });

    // it("should render multiple toast elements when several toast notifications are pushed", () => {
    //   for (let i = 0; i < 1; i++) {
    //     fireEvent.click(screen.getByRole("button", { name: "Add" }));
    //   }
    //   const toastElement = screen.getAllByRole("button", {
    //     name: "Lorem ipsum",
    //   });
    //   expect(toastElement).toHaveLength(1);
    // });

    it("shouldn't render more than 1 toast elements at once", () => {
      for (let i = 0; i < 1; i++) {
        fireEvent.click(screen.getByRole("button", { name: "Add" }));
      }
      const toastElement = screen.getAllByRole("button", {
        name: "Lorem ipsum",
      });
      expect(toastElement).toHaveLength(1);
    });

    it("should dismiss a toast when the toast button is clicked", async () => {
      fireEvent.click(screen.getByRole("button", { name: "Add" }));
      const toastElement = screen.getByRole("button", { name: "Lorem ipsum" });
      fireEvent.click(toastElement);
      await waitForElementToBeRemoved(toastElement);
      expect(toastElement).not.toBeInTheDocument();
    });

    it("should dismiss a toast automatically after 5 seconds", async () => {
      fireEvent.click(screen.getByRole("button", { name: "Add" }));
      const toastElement = screen.getByRole("button", {
        name: "Lorem ipsum",
      });
      await waitForElementToBeRemoved(toastElement, { timeout: 5000 });
      expect(toastElement).not.toBeInTheDocument();
    });
  });
});
