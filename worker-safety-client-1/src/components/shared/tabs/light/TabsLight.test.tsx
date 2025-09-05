import { render } from "@testing-library/react";
import TabsLight from "./TabsLight";

const options = ["Active", "Pending", "Completed"];

describe(TabsLight.name, () => {
  it("should match the snapshot", () => {
    const { asFragment } = render(
      <TabsLight options={options} onSelect={jest.fn()} />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
