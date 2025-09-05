import { render, screen } from "@testing-library/react";
import Input from "./Input";

describe(Input.name, () => {
  it("should render correctly", () => {
    const { asFragment } = render(<Input type="text" />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render an icon when passed as prop", () => {
    const icon = "dashboard";
    const { asFragment } = render(<Input type="text" icon={icon} />);
    expect(
      document.querySelector("[aria-hidden]")?.classList.contains(`ci-${icon}`)
    ).toBeTruthy();

    expect(asFragment()).toMatchSnapshot();
  });

  it("should outline the input when has an error", () => {
    render(<Input type="text" error="some error" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  describe("when input is disabled", () => {
    it("should be disabled", () => {
      render(<Input type="text" disabled />);
      expect(screen.getByRole("textbox")).toBeDisabled();
    });

    it("should render the input text disabled", () => {
      const { asFragment } = render(<Input type="text" disabled />);

      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when input is readOnly", () => {
    it("should be readonly and not have borders", () => {
      const { asFragment } = render(
        <Input type="text" readOnly defaultValue="Lorem ipsum" />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
