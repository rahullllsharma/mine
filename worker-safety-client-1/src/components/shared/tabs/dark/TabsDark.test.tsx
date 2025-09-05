import { render } from "@testing-library/react";
import TabsDark from "./TabsDark";

const options = ["Active", "Pending", "Completed"];

describe(TabsDark.name, () => {
  it("should match the snapshot", () => {
    const { asFragment } = render(
      <TabsDark options={options} onSelect={jest.fn()} />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
