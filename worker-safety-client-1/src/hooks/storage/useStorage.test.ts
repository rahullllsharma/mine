import type { StorageType } from "./useStorage";
import { useStorage } from "./useStorage";

const storageTypes: StorageType[] = ["local", "session"];

Object.defineProperty(window, "localStorage", {
  value: {
    getItem: jest.fn(() => null),
    setItem: jest.fn(() => null),
  },
  writable: true,
});
Object.defineProperty(window, "sessionStorage", {
  value: {
    getItem: jest.fn(() => null),
    setItem: jest.fn(() => null),
  },
  writable: true,
});

describe(useStorage.name, () => {
  describe.each(storageTypes)("when using %s", type => {
    const storage =
      type === "local" ? window.localStorage : window.sessionStorage;

    it("should call setItem", () => {
      const { store } = useStorage(type);
      store("mapFilters", "data");

      expect(storage.setItem).toHaveBeenCalledTimes(1);
    });

    it("should call getItem", () => {
      const { read } = useStorage(type);
      read("mapFilters");

      expect(storage.getItem).toHaveBeenCalledTimes(1);
    });
  });
});
