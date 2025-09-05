// HTTP Status Codes Constants
export const HTTP_STATUS_CODES = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  MOVED_PERMANENTLY: 301,
  FOUND: 302,
  NOT_MODIFIED: 304,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  NOT_IMPLEMENTED: 501,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  PDF_DOWNLOAD_EDIT_MODE:
    "You cannot download the PDF while the form is in Edit mode. Please save or cancel your changes first",
  PDF_DOWNLOAD_FORBIDDEN: "You don't have permission to download this PDF",
  PDF_DOWNLOAD_NOT_FOUND: "The requested form was not found",
  PDF_DOWNLOAD_GENERIC: "Failed to download PDF. Please try again later",
  FORM_NOT_FOUND: "Form not found",
  FORM_ACCESS_DENIED: "You don't have permission to access this form",
  FORM_SAVE_ERROR: "Failed to save form. Please try again",
  FORM_DELETE_ERROR: "Failed to delete form. Please try again",
  NETWORK_ERROR: "Network error. Please check your connection and try again",
  SERVER_ERROR: "Server error. Please try again later",
  TIMEOUT_ERROR: "Request timed out. Please try again",
  SESSION_EXPIRED: "Your session has expired. Please log in again",
  INVALID_CREDENTIALS: "Invalid username or password",
  ACCESS_DENIED:
    "Access denied. You don't have permission to perform this action",
} as const;

// Error Code to Message Mapping
export const ERROR_CODE_MESSAGES = {
  [HTTP_STATUS_CODES.BAD_REQUEST]: ERROR_MESSAGES.FORM_SAVE_ERROR,
  [HTTP_STATUS_CODES.UNAUTHORIZED]: ERROR_MESSAGES.SESSION_EXPIRED,
  [HTTP_STATUS_CODES.FORBIDDEN]: ERROR_MESSAGES.ACCESS_DENIED,
  [HTTP_STATUS_CODES.NOT_FOUND]: ERROR_MESSAGES.FORM_NOT_FOUND,
  [HTTP_STATUS_CODES.CONFLICT]: ERROR_MESSAGES.PDF_DOWNLOAD_EDIT_MODE,
  [HTTP_STATUS_CODES.UNPROCESSABLE_ENTITY]: ERROR_MESSAGES.FORM_SAVE_ERROR,
  [HTTP_STATUS_CODES.TOO_MANY_REQUESTS]:
    "Too many requests. Please wait and try again",
  [HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR]: ERROR_MESSAGES.SERVER_ERROR,
  [HTTP_STATUS_CODES.SERVICE_UNAVAILABLE]: ERROR_MESSAGES.SERVER_ERROR,
} as const;

export const PDF_DOWNLOAD_ERRORS = {
  EDIT_MODE: {
    status: HTTP_STATUS_CODES.CONFLICT,
    message: ERROR_MESSAGES.PDF_DOWNLOAD_EDIT_MODE,
  },
  FORBIDDEN: {
    status: HTTP_STATUS_CODES.FORBIDDEN,
    message: ERROR_MESSAGES.PDF_DOWNLOAD_FORBIDDEN,
  },
  NOT_FOUND: {
    status: HTTP_STATUS_CODES.NOT_FOUND,
    message: ERROR_MESSAGES.PDF_DOWNLOAD_NOT_FOUND,
  },
} as const;

export const getErrorMessage = (statusCode: number): string => {
  return (
    ERROR_CODE_MESSAGES[statusCode as keyof typeof ERROR_CODE_MESSAGES] ||
    ERROR_MESSAGES.SERVER_ERROR
  );
};

// Error type definitions
export interface HttpError {
  response?: {
    status: number;
    data?: unknown;
    statusText?: string;
  };
  request?: unknown;
  message: string;
}

// Type guard to check if error is HttpError
export const isHttpError = (error: unknown): error is HttpError => {
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof (error as HttpError).message === "string"
  );
};

// Helper function to check if error is a specific type
export const isNetworkError = (error: HttpError): boolean => {
  return !error.response && !!error.request;
};

// Check if error has HTTP response
export const hasHttpResponse = (
  error: HttpError
): error is HttpError & { response: NonNullable<HttpError["response"]> } => {
  return !!error.response;
};

export const isServerError = (statusCode: number): boolean => {
  return statusCode >= 500 && statusCode < 600;
};

export const isClientError = (statusCode: number): boolean => {
  return statusCode >= 400 && statusCode < 500;
};

// Safe way to get status code from error
export const getStatusCode = (error: HttpError): number | undefined => {
  return hasHttpResponse(error) ? error.response.status : undefined;
};

// Safe error message extractor for unknown errors
export const getSafeErrorMessage = (error: unknown): string => {
  if (isHttpError(error)) {
    const statusCode = getStatusCode(error);
    return statusCode ? getErrorMessage(statusCode) : error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return ERROR_MESSAGES.SERVER_ERROR;
};
