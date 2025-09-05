import { useAuthStore } from "./useAuthStore.store";

const originalState = useAuthStore.getState();

describe(useAuthStore.name, () => {
  beforeEach(() => {
    useAuthStore.setState(originalState);
  });

  describe("setUser", () => {
    it("should set an user", () => {
      const { setUser } = useAuthStore.getState();
      setUser({
        id: "123",
        initials: "JD",
        name: "John Doe",
        email: "super@email.local.urbinternal.com",
        permissions: [],
        role: "administrator",
        opco: null,
        userPreferences: [],
      });

      const { me } = useAuthStore.getState();

      expect(me.name).toEqual("John Doe");
      expect(me.initials).toEqual("JD");
      expect(me.id).toEqual("123");
    });
  });

  describe("isAdmin", () => {
    it('should return "true" if user role is administrator', () => {
      useAuthStore.setState(state => ({
        ...state,
        me: {
          id: "123",
          initials: "JD",
          name: "John Doe",
          email: "super@email.local.urbinternal.com",
          permissions: [],
          role: "administrator",
          opco: null,
          userPreferences: [],
        },
      }));
      expect(useAuthStore.getState().isAdmin).toBeTruthy();
    });

    it('should return "false" if user role is administrator', () => {
      useAuthStore.setState(state => ({
        ...state,
        me: {
          id: "123",
          initials: "JD",
          name: "John Doe",
          email: "super@email.local.urbinternal.com",

          permissions: [],
          role: "manager",
          opco: null,
          userPreferences: [],
        },
      }));
      expect(useAuthStore.getState().isAdmin).toBeTruthy();
    });
  });

  describe("hasPermission", () => {
    it('should return "true" if the permission array contains a given permission', () => {
      useAuthStore.setState(state => ({
        ...state,
        me: {
          id: "123",
          initials: "JD",
          name: "John Doe",
          email: "super@email.local.urbinternal.com",

          permissions: ["ADD_CONTROLS", "ADD_HAZARDS", "ADD_PROJECTS"],
          role: "manager",
          opco: null,
          userPreferences: [],
        },
      }));

      expect(
        useAuthStore.getState().hasPermission("ADD_PROJECTS")
      ).toBeTruthy();
    });

    it('should return "false" if the permission array does not contains a given permission', () => {
      useAuthStore.setState(state => ({
        ...state,
        me: {
          id: "123",
          initials: "JD",
          name: "John Doe",
          email: "super@email.local.urbinternal.com",

          permissions: ["ADD_CONTROLS", "ADD_HAZARDS"],
          role: "manager",
          opco: null,
          userPreferences: [],
        },
      }));

      expect(useAuthStore.getState().hasPermission("ADD_PROJECTS")).toBeFalsy();
    });
  });
});
