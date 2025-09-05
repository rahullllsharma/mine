import { screen, render } from "@testing-library/react";
import { RiskLevel } from "@/api/generated/types";

import { TaskCard } from "./TaskCard";

describe(TaskCard.name, () => {
  const props = {
    title: "Install and tensioning anchors/guys - Rigging loads",
  };

  it("renders correctly with high risk", () => {
    const { asFragment } = render(
      <TaskCard {...props} risk={RiskLevel.High} />
    );

    expect(
      screen.getByText("Install and tensioning anchors/guys - Rigging loads")
    ).toBeInTheDocument();
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with medium risk", () => {
    const { asFragment } = render(
      <TaskCard {...props} risk={RiskLevel.Medium} />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with low risk", () => {
    const { asFragment } = render(<TaskCard {...props} risk={RiskLevel.Low} />);

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with recalculating risk", () => {
    const { asFragment } = render(
      <TaskCard {...props} risk={RiskLevel.Recalculating} />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("renders correctly with unknown risk", () => {
    const { asFragment } = render(
      <TaskCard {...props} risk={RiskLevel.Unknown} />
    );

    expect(asFragment()).toMatchSnapshot();
  });
});
