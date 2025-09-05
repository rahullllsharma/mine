import type { UseMutationOptions } from "@tanstack/react-query";
import type { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { useMutation } from "@tanstack/react-query";
import { signIn, useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import axiosRest, { getErrorMessage } from "@/api/restApi";

type Props<T> = {
  endpoint: string | ((data: T) => string);
  method?: "post" | "put" | "delete" | "patch" | "get";
  dtoFn?: (data: T) => unknown;
  axiosConfig?: AxiosRequestConfig;
  axiosInstance?: AxiosInstance;
  mutationOptions?: Omit<
    UseMutationOptions<unknown, AxiosError, T>,
    "mutationFn"
  >;
};

const useRestMutation = <T extends Record<string, unknown>>({
  endpoint,
  method = "delete",
  dtoFn = () => ({}),
  axiosConfig,
  mutationOptions,
  axiosInstance = axiosRest,
}: Props<T>) => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<unknown | null>(null); // Added state for response data

  const { data: session } = useSession({ required: true });

  const { mutate, isLoading, error, reset } = useMutation<
    unknown,
    AxiosError,
    T
  >({
    mutationFn: async data => {
      const url = typeof endpoint === "string" ? endpoint : endpoint(data);
      if (method === "delete") {
        const response = await axiosInstance.delete(url, {
          ...axiosConfig,
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
            ...(axiosConfig?.headers || {}),
          },
        });
        setResponseData(response.data);
        return response;
      } else if (method === "get") {
        const response = await axiosInstance.get(url, {
          ...axiosConfig,
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
            ...(axiosConfig?.headers || {}),
          },
        });
        return response;
      } else {
        const response = await axiosInstance[method](url, dtoFn(data), {
          ...axiosConfig,
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
            ...(axiosConfig?.headers || {}),
          },
        });

        setResponseData(response.data);
        return response;
      }
    },
    ...mutationOptions,
  });

  useEffect(() => {
    // check if refreshToken expired
    if (session?.error) signIn("keycloak", { redirect: true });
    if (error) {
      setResponseData(null);
      // removed for token refresh
      setErrorMessage(getErrorMessage(error));
    } else {
      setErrorMessage(null);
    }
  }, [error, session, axiosConfig]);

  return {
    mutate,
    isLoading,
    error: errorMessage,
    reset,
    responseData,
  };
};

export default useRestMutation;
