import { MockedProvider } from "@apollo/client/testing";
import { formRender } from "@/utils/dev/jest";
import Attachments from "./Attachments";

describe(Attachments.name, () => {
  describe("when the component renders", () => {
    it("should display the attachements section", () => {
      const { asFragment } = formRender(
        <MockedProvider>
          <Attachments />
        </MockedProvider>
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
