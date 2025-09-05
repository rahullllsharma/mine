import type { AuthUser } from "@/types/auth/AuthUser";

/**
 * Checks if the user has permissions to remove ALL reports
 *
 * @param {User} user
 * @returns {boolean}
 */
export const canDeleteReports = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("DELETE_REPORTS");
};

/**
 * Checks if the user has permissions to remove ALL his OWN reports
 *
 * @param {User} user
 * @returns {boolean}
 */
export const canDeleteOwnReport = (
  user: AuthUser,
  reportCreatedUserId: string
): boolean => {
  const { permissions, id } = user ?? {};
  return (
    permissions.includes("DELETE_OWN_REPORTS") && id === reportCreatedUserId
  );
};

export const canEditReports = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("EDIT_REPORTS");
};

export const canEditOwnReport = (
  user: AuthUser,
  reportCreatedUserId: string
): boolean => {
  const { permissions, id } = user;
  return permissions.includes("EDIT_OWN_REPORTS") && id === reportCreatedUserId;
};

export const canReopenReports = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("REOPEN_REPORTS");
};

export const canReopenOwnReport = (
  user: AuthUser,
  reportCreatedUserId: string
): boolean => {
  const { permissions, id } = user;
  return (
    permissions.includes("REOPEN_OWN_REPORT") && id === reportCreatedUserId
  );
};

// TODO: This should be updated when the BE implements the CAN_DOWNLOAD permission.
export const canDownloadReports = (user: AuthUser): boolean => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { role } = user;
  return true;
};

export const canViewReports = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("VIEW_INSPECTIONS");
};

export const canViewProject = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("VIEW_PROJECT");
};

export const canAddReports = (user: AuthUser): boolean => {
  const { permissions } = user ?? {};
  return permissions.includes("ADD_REPORTS");
};
