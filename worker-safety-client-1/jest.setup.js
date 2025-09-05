import "@testing-library/jest-dom/extend-expect";
import nodeCrypto from "crypto";

// Polyfill crypto.getRandomValues for environments where it's not available (e.g., JSDOM)
// Needed by uuid v4 in modules imported during tests
if (!globalThis.crypto) {
  // minimal shim
  globalThis.crypto = {
    getRandomValues: arr => nodeCrypto.randomFillSync(arr),
  };
} else if (!globalThis.crypto.getRandomValues) {
  globalThis.crypto.getRandomValues = arr => nodeCrypto.randomFillSync(arr);
}
