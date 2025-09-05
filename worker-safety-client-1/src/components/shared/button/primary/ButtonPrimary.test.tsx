import { render, screen } from "@testing-library/react";
import React from "react";
import ButtonPrimary from "./ButtonPrimary";

describe("ButtonPrimary", () => {
  describe("when is rendered", () => {
    beforeEach(() => {
      render(<ButtonPrimary label="ok" />);
    });

    it("should be in the document", () => {
      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("should contain Urbint brand color", () => {
      expect(screen.getByRole("button")).toHaveClass("bg-brand-urbint-40");
    });

    it("should render a regular size button by default", () => {
      expect(screen.getByRole("button")).toHaveClass("text-base");
    });
  });

  describe("when button size is large", () => {
    it("should render a large button", () => {
      render(<ButtonPrimary label="ok" size="lg" />);
      expect(screen.getByRole("button")).toHaveClass("text-lg");
    });
  });

  describe("when button size is small", () => {
    it("should render a small button", () => {
      render(<ButtonPrimary label="ok" size="sm" />);
      expect(screen.getByRole("button")).toHaveClass("text-sm");
    });
  });

  describe("when is disabled", () => {
    it("should have the attribute disabled", () => {
      render(<ButtonPrimary disabled label="ok" />);

      expect(screen.getByRole("button")).toBeDisabled();
    });
  });
});
