import type { TruncatedTextProps } from "./TruncatedText";
import { screen, render, fireEvent } from "@testing-library/react";
import { TruncatedText } from "./TruncatedText";

describe(TruncatedText.name, () => {
  const props: TruncatedTextProps = {
    text: "This is a test with a long string really looooooong",
    maxCharacters: 4,
    showEllipsis: true,
  };

  it("renders correctly with text truncated", () => {
    render(<TruncatedText {...props} />);

    expect(screen.getByText("This...")).toBeInTheDocument();
    expect(screen.getByText("Show More")).toBeInTheDocument();
  });

  it("renders full text if text length is smaller than maxCharacters", () => {
    render(<TruncatedText {...props} maxCharacters={100} />);

    expect(
      screen.getByText("This is a test with a long string really looooooong")
    ).toBeInTheDocument();
    expect(screen.queryByText("Show More")).not.toBeInTheDocument();
  });

  describe("User interaction", () => {
    it("shows full text when clicking on Show More / Show Less", () => {
      render(<TruncatedText {...props} />);

      const showMoreButton = screen.getByText("Show More");

      fireEvent.click(showMoreButton);

      expect(
        screen.getByText("This is a test with a long string really looooooong")
      ).toBeInTheDocument();
      expect(screen.getByText("Show Less")).toBeInTheDocument();

      const showLess = screen.getByText("Show Less");
      fireEvent.click(showLess);

      expect(screen.getByText("This...")).toBeInTheDocument();
      expect(screen.getByText("Show More")).toBeInTheDocument();
    });
  });
});
