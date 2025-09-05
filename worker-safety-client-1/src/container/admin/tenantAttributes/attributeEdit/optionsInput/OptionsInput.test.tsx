import { screen } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import { OptionsInput } from "./OptionsInput";

describe(OptionsInput.name, () => {
  describe("when mandatory is set as true", () => {
    beforeEach(() => {
      formRender(<OptionsInput />, {
        mandatory: true,
        options: [{ key: "visible", value: true }],
      });
    });

    it("should set the visible checkbox as disabled", () => {
      const checkboxElement = screen.getByRole("checkbox", {
        name: /visible/i,
      }) as HTMLInputElement;
      expect(checkboxElement.disabled).toBe(true);
    });

    it("should keep the visible checkbox as checked", () => {
      const checkboxElement = screen.getByRole("checkbox", {
        name: /visible/i,
      }) as HTMLInputElement;
      expect(checkboxElement.defaultChecked).toBe(true);
    });

    it("should render the extra caption", () => {
      screen.getByText("This attribute is mandatory.");
    });
  });

  describe("when mandatory is set as false", () => {
    beforeEach(() => {
      formRender(<OptionsInput />, {
        mandatory: false,
        options: [{ key: "visible", value: true }],
      });
    });

    it("should not have any disabled checkboxes", () => {
      screen.getAllByRole("checkbox", { checked: true });
    });

    it("should not display the extra caption", () => {
      const submitButton = screen.queryByText("This attribute is mandatory.");
      expect(submitButton).toBeNull();
    });
  });
});
