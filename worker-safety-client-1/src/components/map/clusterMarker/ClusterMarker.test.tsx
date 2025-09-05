import { render, screen } from "@testing-library/react";
import ClusterMarker from "./ClusterMarker";

describe(ClusterMarker.name, () => {
  it("render correctly", () => {
    const { asFragment } = render(
      <ClusterMarker high={25} medium={25} low={25} unknown={25} />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it.each`
    high  | medium       | low          | unknown
    ${25} | ${25}        | ${25}        | ${25}
    ${25} | ${25}        | ${25}        | ${undefined}
    ${25} | ${25}        | ${undefined} | ${undefined}
    ${25} | ${undefined} | ${undefined} | ${undefined}
    ${25} | ${25}        | ${25}        | ${25}
    ${25} | ${25}        | ${25}        | ${0}
    ${25} | ${25}        | ${0}         | ${0}
    ${25} | ${0}         | ${0}         | ${0}
  `("should include a total and the risks passed", props => {
    const params = Object.entries(props) as [string, number | undefined][];
    const total = params.reduce((acc, [, val]) => acc + (val ?? 0), 0);
    const totalRiskUsed = params.reduce((acc, [, v]) => acc + (v ? 1 : 0), 0);

    render(<ClusterMarker {...props} />);

    expect(document.querySelectorAll("path")).toHaveLength(totalRiskUsed);

    // Make sure the proper risk exists in the document
    params
      .filter(([, value]) => !!value)
      .forEach(([param]) => {
        expect(
          document.querySelector(`.text-risk-${param}`)
        ).toBeInTheDocument();
      });

    screen.getByText(total);
  });
});
