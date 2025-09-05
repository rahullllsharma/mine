import {
  completedNavigationStyles,
  defaultNavigationStyles,
  errorNavigationStyles,
  getNavigationStyles,
} from "./navigation.utils";

describe("Navigation Helper", () => {
  describe("getNavigationStyles", () => {
    it("should match the default styles, if no status is passed as a prop", () => {
      const navStyles = getNavigationStyles();
      expect(navStyles).toEqual(defaultNavigationStyles);
    });

    it('should match the default styles, when status is "default"', () => {
      const navStyles = getNavigationStyles("default");
      expect(navStyles).toEqual(defaultNavigationStyles);
    });

    it('should match the completed styles, when status is "completed"', () => {
      const navStyles = getNavigationStyles("completed");
      expect(navStyles).toEqual(completedNavigationStyles);
    });

    it('should match the error styles, when status is "error"', () => {
      const navStyles = getNavigationStyles("error");
      expect(navStyles).toEqual(errorNavigationStyles);
    });
  });
});
