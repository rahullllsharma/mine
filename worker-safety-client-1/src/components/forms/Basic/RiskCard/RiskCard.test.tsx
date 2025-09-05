import type { RiskCardProps } from "./RiskCard";
import { render } from "@testing-library/react";

import { RiskCard } from "./RiskCard";

describe(RiskCard.name, () => {
  const props: RiskCardProps = {
    risk: "ArcFlash",
  };

  it("renders correctly", () => {
    const { asFragment } = render(<RiskCard {...props} />);

    expect(asFragment()).toMatchSnapshot();
  });
});
