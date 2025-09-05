import { render, screen } from "@testing-library/react";
import * as reactMapGl from "react-map-gl";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import LocationMarker from "./LocationMarker";

jest.mock("react-map-gl");

describe(LocationMarker.name, () => {
  beforeEach(() => {
    // the real <Marker /> depends on a context from the Map and the way this is implemented
    // makes it hard to wrapper the provider. In the end, we'd mock everything just to achieve
    // the same result as mock the <Marker />

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    reactMapGl.Marker = jest.fn(({ children }) => children || <></>);
  });

  it("should render correctly", () => {
    render(
      <LocationMarker longitude={1} latitude={1} riskLevel={RiskLevel.HIGH} />
    );

    screen.getByTestId("map-marker");
  });
});
