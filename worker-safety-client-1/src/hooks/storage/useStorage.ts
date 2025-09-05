type StorageType = "local" | "session";

//Keys allowed by WS
export type StorageKey = "mapFilters" | "lastVisitedTemplateId";

const getStorage = (type: StorageType) =>
  type === "local" ? localStorage : sessionStorage;

function useStorage(type: StorageType) {
  const store = (key: StorageKey, data: string) => {
    const storage = getStorage(type);
    storage.setItem(key, data);
  };

  const read = (key: StorageKey): string => {
    const storage = getStorage(type);
    const storageValue = storage.getItem(key);

    return storageValue ?? "";
  };

  const clear = (key: StorageKey) => {
    const storage = getStorage(type);
    storage.removeItem(key);
  };

  return { store, read, clear };
}

function useLocalStorage() {
  return useStorage("local");
}

function useSessionStorage() {
  return useStorage("session");
}

export { useStorage, useLocalStorage, useSessionStorage };
export type { StorageType };
