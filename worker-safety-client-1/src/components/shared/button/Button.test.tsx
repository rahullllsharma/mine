import { render, screen } from "@testing-library/react";
import React from "react";
import Button from "./Button";

describe("ButtonPrimary", () => {
  it("should be in the document", () => {
    const { getByRole } = render(<Button label="ok" />);

    expect(getByRole("button")).toBeInTheDocument();
  });

  describe("when is disabled", () => {
    it("should have the attribute disabled", () => {
      const { getByRole } = render(<Button disabled label="ok" />);
      expect(getByRole("button")).toBeDisabled();
    });
  });

  describe("when it's loading", () => {
    it("should show the loading spinner", () => {
      const { asFragment } = render(<Button loading label="ok" />);

      expect(screen.getByRole("button")).toBeDisabled();
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when contain icons", () => {
    describe("when is passed a left icon", () => {
      it("should contain an icon as first child", () => {
        const { asFragment } = render(
          <Button label="ok" iconStart="chevron_duo_up" />
        );
        expect(asFragment()).toMatchSnapshot();
      });
    });
    describe("when is passed a right icon", () => {
      it("should contain an icon as last child", () => {
        const { asFragment } = render(
          <Button label="ok" iconEnd="chevron_duo_up" />
        );
        expect(asFragment()).toMatchSnapshot();
      });
    });
    describe("when is passed a left and right icon", () => {
      it("should contain both icons", () => {
        const { asFragment } = render(
          <Button
            label="ok"
            iconStart="chevron_duo_up"
            iconEnd="chevron_duo_up"
          />
        );
        expect(asFragment()).toMatchSnapshot();
      });
    });
  });
});
