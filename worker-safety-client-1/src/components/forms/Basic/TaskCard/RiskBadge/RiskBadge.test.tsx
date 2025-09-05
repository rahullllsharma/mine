import { render, screen } from "@testing-library/react";
import { RiskLevel } from "@/api/generated/types";

import { RiskBadge } from "./RiskBadge";

describe(RiskBadge.name, () => {
  const props = (risk: RiskLevel) => ({
    risk,
    label: `${risk} risk`,
  });

  it("renders properly the high risk badge", () => {
    const { asFragment } = render(<RiskBadge {...props(RiskLevel.High)} />);

    expect(screen.getByText("HIGH RISK"));
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders properly the medium risk badge", () => {
    const { asFragment } = render(<RiskBadge {...props(RiskLevel.Medium)} />);

    expect(screen.getByText("MEDIUM RISK"));
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders properly the low risk badge", () => {
    const { asFragment } = render(<RiskBadge {...props(RiskLevel.Low)} />);

    expect(screen.getByText("LOW RISK"));
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders properly the unknown risk badge", () => {
    const { asFragment } = render(<RiskBadge {...props(RiskLevel.Unknown)} />);

    expect(screen.getByText("UNKNOWN RISK"));
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders properly the recalculating risk badge", () => {
    const { asFragment } = render(
      <RiskBadge {...props(RiskLevel.Recalculating)} />
    );

    expect(screen.getByText("RECALCULATING RISK"));
    expect(asFragment()).toMatchSnapshot();
  });
});
