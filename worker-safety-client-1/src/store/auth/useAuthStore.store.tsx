import type { LocationFilter } from "@/container/mapView/filters/mapFilters/MapFilters";
import type {
  AuthUser,
  UserPermission,
  UserPreferenceFormFilters,
  UserPreferenceLocationMapFilters,
  UserPreferenceCWFTemplateFormFilters,
} from "@/types/auth/AuthUser";
import type { FormFilter } from "@/container/insights/filters/formFilters/FormFilters";
import type { TemplateFormsFilter } from "@/components/templatesComponents/filter/TemplateFormFilters";
import create from "zustand";

type AuthStore = {
  me: AuthUser;
  setUser: (u: AuthUser | ((p: AuthUser) => AuthUser)) => void;
  isAdmin: () => boolean;
  isSupervisor: () => boolean;
  isManager: () => boolean;
  isViewer: () => boolean;
  hasPermission: (permission: UserPermission) => boolean;
  getLocationMapFilters: () => LocationFilter[] | null;
  setLocationMapFilters: (f: LocationFilter[]) => void;
  getFormFilters: () => FormFilter[] | null;
  getCwfTemplateFormFilters: () => TemplateFormsFilter[] | null;
};

function isMapPref(p: unknown): p is UserPreferenceLocationMapFilters {
  return (
    typeof p === "object" &&
    p !== null &&
    (p as any).entityType === "MapFilters"
  );
}
function isCWFPref(p: unknown): p is UserPreferenceCWFTemplateFormFilters {
  if (typeof p !== "object" || p === null) return false;
  const maybe = p as { entityType?: unknown };
  return maybe.entityType === "CWFTemplateFormFilters";
}
const defaultUser: AuthUser = {
  id: "0",
  initials: "",
  name: "",
  email: "",
  role: "viewer",
  permissions: [],
  opco: null,
  userPreferences: [],
};

const useAuthStore = create<AuthStore>()((set, get) => ({
  me: defaultUser,

  setUser: updater =>
    set(s => ({ me: typeof updater === "function" ? updater(s.me) : updater })),
  isAdmin: () => get().me.role === "administrator",
  isSupervisor: () => get().me.role === "supervisor",
  isManager: () => get().me.role === "manager",
  isViewer: () => get().me.role === "viewer",
  hasPermission: p => get().me.permissions.includes(p),
  getLocationMapFilters: () => {
    const pref = get().me.userPreferences?.find(isMapPref);
    return pref?.contents ?? null;
  },

  getFormFilters: () =>
    (
      get().me.userPreferences?.find(
        ({ entityType }) => entityType === "FormFilters"
      ) as UserPreferenceFormFilters
    )?.contents,

  setLocationMapFilters: filters => {
    set(state => {
      const existing = state.me.userPreferences?.find(isMapPref) as
        | UserPreferenceLocationMapFilters
        | undefined;

      const updatedPref: UserPreferenceLocationMapFilters = existing
        ? { ...existing, contents: filters }
        : {
            id: "local-map-pref",
            entityType: "MapFilters",
            contents: filters,
          };

      return {
        me: {
          ...state.me,
          userPreferences: [
            ...(state.me.userPreferences?.filter(
              p => p.entityType !== "MapFilters"
            ) ?? []),
            updatedPref,
          ],
        },
      };
    });
  },
  getCwfTemplateFormFilters: () =>
    get().me.userPreferences?.find(isCWFPref)?.contents ?? null,
}));
export { useAuthStore };
