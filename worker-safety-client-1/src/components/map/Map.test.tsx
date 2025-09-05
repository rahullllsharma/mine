import { render, screen } from "@testing-library/react";
import React from "react";
import * as reactMapGl from "react-map-gl";
import Map from "./Map";

jest.mock("react-map-gl");

jest.mock("next-auth/react", () => {
  const originalModule = jest.requireActual("next-auth/react");
  const mockSession = {
    expires: new Date(Date.now() + 2 * 86400).toISOString(),
    user: { username: "admin" },
  };
  return {
    __esModule: true,
    ...originalModule,
    useSession: jest.fn(() => {
      return { data: mockSession, status: "authenticated" }; // return type is [] in v3 but changed to {} in v4
    }),
  };
});

describe(Map.name, () => {
  beforeEach(() => {
    // This will "omit" issue
    // Error: Map is not supported by this browser
    jest.spyOn(window.console, "error").mockImplementation(undefined);

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    reactMapGl.default = jest.fn(({ children }) => <>{children}</>);
  });

  it("should render the map", () => {
    render(<Map mapboxAccessToken="xpto" />);
    screen.getByTestId("map");
  });

  it("should render children inside the map", () => {
    render(
      <Map mapboxAccessToken="xpto">
        <p>hello</p>
      </Map>
    );

    screen.getByTestId("map");
    screen.getByText(/hello/gi);
  });

  it("should throw an error when the api key is missing", () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    expect(() => render(<Map />)).toThrowError();
  });
});
