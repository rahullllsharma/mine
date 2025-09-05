import {
  pushHistoryStateQueryParam,
  replaceHistoryStateQueryParam,
} from "./router.utils";

describe("router helper", () => {
  let cacheHistoryState: History;
  const url = "projects/8461eec0-d045-4833-bcee-6eadd0722974";

  beforeEach(() => {
    cacheHistoryState = window.history;

    Object.defineProperty(window, "history", {
      value: {
        replaceState: jest.fn(),
        pushState: jest.fn(),
        state: {
          as: url,
        },
      },
      writable: true,
    });
  });

  afterEach(() => {
    Object.defineProperties(
      window.history,
      cacheHistoryState as unknown as PropertyDescriptorMap
    );
  });

  it("should append the location query param to the URL in the browser history", () => {
    pushHistoryStateQueryParam("location", "some-id");
    const expectedNewUrl = "/?location=some-id";

    expect(global.history.pushState).toHaveBeenCalledWith(
      { ...global.history.state, as: expectedNewUrl, url: expectedNewUrl },
      "",
      "/?location=some-id"
    );
  });

  it("should replace the location query param to the URL in the browser history", () => {
    replaceHistoryStateQueryParam("location", "some-id");
    const expectedNewUrl = "/?location=some-id";

    expect(global.history.replaceState).toHaveBeenCalledWith(
      { ...global.history.state, as: expectedNewUrl, url: expectedNewUrl },
      "",
      "/?location=some-id"
    );
  });
});
