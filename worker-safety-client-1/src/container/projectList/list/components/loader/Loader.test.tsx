import { act, render, screen } from "@testing-library/react";
import { mockIntersectionObserver } from "jsdom-testing-mocks";
import { Loader } from "./Loader";

const io = mockIntersectionObserver();

describe(Loader.name, () => {
  it("should render correctly", () => {
    const { asFragment } = render(
      <Loader onLoadMore={jest.fn()} shouldLoadMore isLoading />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  describe("when the component is NOT on the screen", () => {
    it.each([
      { shouldLoadMore: false, isLoading: false },
      { shouldLoadMore: true, isLoading: false },
      { shouldLoadMore: false, isLoading: false },
      { shouldLoadMore: true, isLoading: true },
    ])(
      "should NOT trigger the onLoadMore callback when it is not intersecting",
      ({ shouldLoadMore, isLoading }) => {
        const mockOnLoadMore = jest.fn();
        render(
          <Loader
            onLoadMore={mockOnLoadMore}
            shouldLoadMore={shouldLoadMore}
            isLoading={isLoading}
          />
        );

        expect(mockOnLoadMore).not.toHaveBeenCalled();
      }
    );
  });

  describe("when the component is visible", () => {
    it("should NOT trigger the onLoadMore callback when skipping", () => {
      const mockOnLoadMore = jest.fn();

      render(
        <Loader
          onLoadMore={mockOnLoadMore}
          shouldLoadMore={false}
          isLoading={false}
        />
      );

      act(() => {
        io.enterNode(screen.getByTestId("list-project-loader"));
      });

      expect(screen.getByTestId("list-project-loader")).toBeInTheDocument();
      expect(mockOnLoadMore).not.toHaveBeenCalled();
    });

    it("should NOT trigger the onLoadMore callback when it is already loading", () => {
      const mockOnLoadMore = jest.fn();

      render(<Loader onLoadMore={mockOnLoadMore} shouldLoadMore isLoading />);

      act(() => {
        io.enterNode(screen.getByTestId("list-project-loader"));
      });

      expect(screen.getByTestId("list-project-loader")).toBeInTheDocument();
      expect(mockOnLoadMore).not.toHaveBeenCalled();
    });

    it("should trigger the onLoadMore callback when it is NOT loading and is NOT skipping", () => {
      const mockOnLoadMore = jest.fn();

      render(
        <Loader onLoadMore={mockOnLoadMore} shouldLoadMore isLoading={false} />
      );

      act(() => {
        io.enterNode(screen.getByTestId("list-project-loader"));
      });

      expect(screen.getByTestId("list-project-loader")).toBeInTheDocument();
      expect(mockOnLoadMore).toHaveBeenCalled();
    });
  });

  describe("when the component enter the screen and left", () => {
    it("should NOT re-trigger onLoadMore callbacks", () => {
      const mockOnLoadMore = jest.fn();

      const { rerender } = render(
        <Loader onLoadMore={mockOnLoadMore} shouldLoadMore isLoading={false} />
      );

      act(() => {
        io.enterNode(screen.getByTestId("list-project-loader"));
      });

      rerender(
        <Loader onLoadMore={mockOnLoadMore} shouldLoadMore isLoading={true} />
      );
      act(() => {
        io.enterNode(screen.getByTestId("list-project-loader"));
      });

      rerender(
        <Loader onLoadMore={mockOnLoadMore} shouldLoadMore isLoading={false} />
      );

      act(() => {
        io.leaveNode(screen.getByTestId("list-project-loader"));
      });

      expect(mockOnLoadMore).toHaveBeenCalledTimes(1);
    });
  });
});
