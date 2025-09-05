import { render, screen } from "@testing-library/react";
import { mockIntersectionObserver } from "jsdom-testing-mocks";
import { useProjects } from "@/hooks/useProjects";
import { mockTenantStore } from "@/utils/dev/jest";
import { List as ProjectsList } from "./List";

// eslint-disable-next-line react-hooks/rules-of-hooks
const projects = useProjects();
mockIntersectionObserver();

describe(ProjectsList.name, () => {
  beforeAll(() => {
    mockTenantStore();
  });

  it("should render correctly", () => {
    const { asFragment } = render(<ProjectsList projects={projects} />);
    expect(asFragment()).toMatchSnapshot();
  });

  describe("<ListInfiniteLoader />", () => {
    it("should render the component when onLoadMore callback is defined and it can still load more data", () => {
      render(<ProjectsList projects={projects} onLoadMore={jest.fn()} />);
      expect(screen.getByTestId("list-project-loader")).toBeInTheDocument();
    });

    it("should not render the component when onLoadMore callback is not defined", async () => {
      render(<ProjectsList projects={projects} />);
      expect(
        await screen.queryByTestId("list-project-loader")
      ).not.toBeInTheDocument();
    });

    it("should remove component when there is nothing more to fetch", async () => {
      render(
        <ProjectsList
          projects={projects}
          state="complete"
          onLoadMore={jest.fn()}
        />
      );

      expect(
        screen.queryByTestId("list-project-loader")
      ).not.toBeInTheDocument();
    });

    it("should remove the component after loading all data available", async () => {
      const { rerender } = render(
        <ProjectsList projects={projects} onLoadMore={jest.fn()} />
      );

      expect(
        await screen.findByTestId("list-project-loader")
      ).toBeInTheDocument();

      rerender(
        <ProjectsList
          projects={projects}
          state="loading"
          onLoadMore={jest.fn()}
        />
      );
      expect(
        await screen.findByTestId("list-project-loader")
      ).toBeInTheDocument();

      rerender(
        <ProjectsList
          projects={projects}
          state="complete"
          onLoadMore={jest.fn()}
        />
      );

      expect(
        await screen.queryByTestId("list-project-loader")
      ).not.toBeInTheDocument();
    });
  });
});
