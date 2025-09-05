import { render, screen } from "@testing-library/react";
import ButtonDanger from "./ButtonDanger";

describe(ButtonDanger.name, () => {
  describe("when is rendered", () => {
    beforeEach(() => {
      render(<ButtonDanger label="ok" />);
    });

    it("should be in the document", () => {
      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("should contain 'system-error-40' color", () => {
      expect(screen.getByRole("button")).toHaveClass("bg-system-error-40");
    });

    it("should render a regular size button by default", () => {
      expect(screen.getByRole("button")).toHaveClass("text-base");
    });
  });

  describe("when button size is large", () => {
    it("should render a large button", () => {
      render(<ButtonDanger label="ok" size="lg" />);
      expect(screen.getByRole("button")).toHaveClass("text-lg");
    });
  });

  describe("when button size is small", () => {
    it("should render a small button", () => {
      render(<ButtonDanger label="ok" size="sm" />);
      expect(screen.getByRole("button")).toHaveClass("text-sm");
    });
  });

  describe("when is disabled", () => {
    it("should have the attribute disabled", () => {
      render(<ButtonDanger disabled label="ok" />);

      expect(screen.getByRole("button")).toBeDisabled();
    });
  });
});
