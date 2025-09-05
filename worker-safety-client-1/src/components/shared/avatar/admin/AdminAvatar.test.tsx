import { render, screen } from "@testing-library/react";
import AdminAvatar from "./AdminAvatar";

describe(AdminAvatar.name, () => {
  describe("when it renders", () => {
    it("should display the urbint icon", () => {
      render(<AdminAvatar />);
      screen.getByRole("img", { name: "Urbint" });
    });
  });
});
