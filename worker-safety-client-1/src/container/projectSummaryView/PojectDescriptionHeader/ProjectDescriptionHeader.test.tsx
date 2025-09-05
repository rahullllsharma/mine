import type { ProjectDescriptionHeaderProps } from "./ProjectDescriptionHeader";
import { render, screen, fireEvent } from "@testing-library/react";
import { ProjectDescriptionHeader } from "./ProjectDescriptionHeader";

describe(ProjectDescriptionHeader.name, () => {
  let props: ProjectDescriptionHeaderProps;

  beforeEach(() => {
    props = {
      description:
        "Test Description bigger than the max characters\nwith break\nlines",
      maxCharacters: 10,
    };
  });

  it("renders properly with truncated title and break lines", () => {
    render(<ProjectDescriptionHeader {...props} />);

    expect(screen.getByText("Test Descr...")).toBeInTheDocument();
  });

  it("renders properly with truncated title and no break lines", () => {
    props.description = "Test Description bigger than the max characters";
    render(<ProjectDescriptionHeader {...props} />);

    expect(screen.getByText("Test Descr...")).toBeInTheDocument();
  });

  it("renders properly with text smaller than the max characters", () => {
    props.description = "Test Description";
    render(<ProjectDescriptionHeader {...props} maxCharacters={50} />);

    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });

  describe("user interaction", () => {
    it("expands when user clicks", () => {
      const description = "This\nhas break\nlines";
      render(<ProjectDescriptionHeader {...props} description={description} />);

      fireEvent.click(screen.getByRole("button"));

      expect(
        screen.getByText(/This\nhas break\nlines/, {
          collapseWhitespace: false,
        })
      ).toHaveTextContent("This has break lines");
    });
  });
});
