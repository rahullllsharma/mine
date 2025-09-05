import { render } from "@testing-library/react";

import { SiteConditionsCard } from "./SiteConditionsCard";

describe(SiteConditionsCard.name, () => {
  it("renders correctly", () => {
    const { asFragment } = render(
      <SiteConditionsCard title="traffic density" />
    );

    expect(asFragment()).toMatchSnapshot();
  });
});
