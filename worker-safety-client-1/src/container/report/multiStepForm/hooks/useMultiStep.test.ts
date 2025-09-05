import { useMultiStepActions, useMultiStepState } from "./useMultiStep";

describe("useMultiStep", () => {
  describe(useMultiStepState.name, () => {
    it.todo("should return all steps");
    it.todo("should return the current active step");
    it.todo("should return true when all steps are completed");
  });
  describe(useMultiStepActions.name, () => {
    describe("before moving to a new section", () => {
      it.todo("should call the onBeforeMove hook");
      it.todo(
        "should NOT dispatch the event if the onBeforeMove hook was cancelled"
      );
      it.todo(
        "should dispatch the event if the onBeforeMove hook was accepted"
      );
    });
  });
});
