import type * as FullStory from "@fullstory/browser";

declare global {
  interface Window {
    FS?: FullStory;
  }
}
