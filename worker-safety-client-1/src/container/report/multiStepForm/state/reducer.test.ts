import reducer from "./reducer";

describe(reducer.name, () => {
  describe("BACK action", () => {
    it.todo("should move to the previous section");
    it.todo("should not move when it is the first section");
  });
  describe("NEXT action", () => {
    it.todo("should move to the next section");
    it.todo("should not move when it is the last section");
  });
  describe("JUMP_TO action", () => {
    it.todo("should move to the defined section");
    it.todo("should not move when section does not exist");
  });
  describe("CHANGE_SECTIONS_STATUS action", () => {
    it.todo("should change to default");
    it.todo("should change to error");
    it.todo("should change to completed");
    it.todo("should default to default when status is not recognized");
  });
  describe("MOVE_FORWARD_AND_COMPLETE action", () => {
    it.todo(
      "should mark the current section completed and move to the next section"
    );
    it.todo(
      "should should mark the current section completed and stay in the current section when it is the last section"
    );
  });
});
