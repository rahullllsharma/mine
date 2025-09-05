import { render } from "@testing-library/react";
import TabsMenuLight from "./TabsMenuLight";

const options = ["Active", "Pending", "Completed"];

describe(TabsMenuLight.name, () => {
  it("should match the snapshot", () => {
    const { asFragment } = render(
      <TabsMenuLight options={options} onSelect={jest.fn()} />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
