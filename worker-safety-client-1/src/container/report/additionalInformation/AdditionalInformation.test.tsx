import { formRender } from "@/utils/dev/jest";
import AdditionalInformation from "./AdditionalInformation";

describe(AdditionalInformation.name, () => {
  describe("when the component renders", () => {
    it("should display two textarea fields", () => {
      const { asFragment } = formRender(<AdditionalInformation />);
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
