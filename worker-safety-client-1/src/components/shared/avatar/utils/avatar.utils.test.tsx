import { getUserInitials } from "./avatar.utils";

describe("InitialsAvatar Helper", () => {
  describe('when "getUserInitials" is called', () => {
    it("with full name should return first letter of first and last names", () => {
      const fullName = "Urbint Admin";

      expect(getUserInitials(fullName)).toStrictEqual("UA");
    });

    it("with initials should return the same initials", () => {
      const initials = "UA";
      expect(getUserInitials(initials)).toStrictEqual("UA");
    });
  });
});
