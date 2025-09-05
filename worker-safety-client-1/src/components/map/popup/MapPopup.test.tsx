import { render, screen } from "@testing-library/react";
import * as reactMapGl from "react-map-gl";
import MapPopup from "./MapPopup";

jest.mock("react-map-gl");

const onCloseHandlerMock = jest.fn();

describe(MapPopup.name, () => {
  beforeEach(() => {
    // the real <Popup /> depends on a context from the Map and the way this is implemented
    // makes it hard to wrapper the provider. In the end, we'd mock everything just to achieve
    // the same result as mock the <Popup />

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    reactMapGl.Popup = jest.fn(({ children }) => children || <></>);
  });

  it("should render correctly", () => {
    render(
      <MapPopup
        longitude={-74.052315}
        latitude={40.703693}
        onClose={onCloseHandlerMock}
      >
        Popup content
      </MapPopup>
    );

    screen.getByText("Popup content");
  });
});
