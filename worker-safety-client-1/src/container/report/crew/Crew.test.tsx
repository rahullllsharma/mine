import { MockedProvider } from "@apollo/client/testing";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import Crew from "./Crew";

describe(Crew.name, () => {
  describe("when the component renders", () => {
    mockTenantStore();
    it("should display the crew section", () => {
      const { asFragment } = formRender(
        <MockedProvider>
          <Crew companies={[]} />
        </MockedProvider>
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
