import type { AxiosError } from "axios";
import axios from "axios";
import { config } from "@/config";

const axiosRest = axios.create({
  baseURL: `${config.workerSafetyServiceUrlRest}/rest`,
});

export enum QUERY_KEYS {
  INSIGHTS = "insights",
}

export const getErrorMessage = (error: AxiosError) => {
  return (
    ((error as AxiosError).response?.data as { detail?: string })?.detail ||
    (error as AxiosError).message
  );
};

export default axiosRest;
