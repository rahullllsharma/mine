import { formRender, mockTenantStore } from "@/utils/dev/jest";
import { PageProvider } from "@/context/PageProvider";
import ProjectDetails from "./ProjectDetails";

describe(ProjectDetails.name, () => {
  mockTenantStore();

  it("should render correctly", () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const { asFragment } = formRender(
      <PageProvider
        props={{
          divisionsLibrary: [],
          regionsLibrary: [],
          projectTypesLibrary: [],
          assetTypesLibrary: [],
          managers: [],
          supervisors: [],
          contractors: [],
        }}
      >
        <ProjectDetails />
      </PageProvider>
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
