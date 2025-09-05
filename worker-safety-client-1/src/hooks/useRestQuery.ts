import type { UseQueryOptions } from "@tanstack/react-query";
import type { AxiosRequestConfig, AxiosInstance } from "axios";
import { AxiosError } from "axios";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { signIn, useSession } from "next-auth/react";
import { StatusCodes } from "http-status-codes";
import axiosRest, { getErrorMessage } from "@/api/restApi";

type Props<T, S> = {
  key: string[];
  endpoint: string;
  axiosConfig?: AxiosRequestConfig;
  axiosInstance?: AxiosInstance;
  queryOptions?: Omit<
    UseQueryOptions<T, AxiosError, S, string[]>,
    "queryFn" | "queryKey"
  >;
};

// Relax generic constraints to support arrays and primitives
const useRestQuery = <T, S = T>({
  key,
  endpoint,
  axiosConfig,
  axiosInstance = axiosRest,
  queryOptions = {},
}: Props<T, S>) => {
  const { data: session } = useSession({ required: true });
  const router = useRouter();

  const { data, isLoading, error, refetch } = useQuery<
    T,
    AxiosError,
    S,
    string[]
  >({
    queryKey: [...key, session?.accessToken ?? ""],
    queryFn: async () => {
      if (session?.error) await signIn("keycloak", { redirect: true });
      try {
        const config = {
          ...axiosConfig,
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
            ...(axiosConfig?.headers || {}),
          },
          validateStatus: function (_status: number) {
            return true;
          },
        };

        const response = await axiosInstance.get(endpoint, config);
        if (response.status >= 200 && response.status < 300) {
          return response.data;
        } else if (response.status === StatusCodes.NOT_FOUND) {
          router.push("/404");
        } else {
          throw new AxiosError(
            `API error with status code: ${response.status}`,
            String(response.status),
            config,
            null,
            response
          );
        }
      } catch (err) {
        throw err;
      }
    },
    ...queryOptions,
  });

  const errorMessage = error ? getErrorMessage(error) : null;

  return {
    data,
    isLoading,
    error: errorMessage,
    refetch,
  };
};

export default useRestQuery;
