import type { APIRequestContext, APIResponse } from "@playwright/test";
import type { AxiosResponse } from "axios";

import axios from "axios";

type CustomAxiosResponse = Pick<
  AxiosResponse<any, any>,
  "status" | "statusText" | "data"
> &
  Partial<AxiosResponse<any, any>> & { ok: boolean };

// Functions
/**
 * Function that returns the API token using axios
 * @returns token
 */
async function getAPIAccessToken(): Promise<string> {
  const {
    data: { access_token: token },
  } = await axios.post(
    `${process.env.KEYCLOAK_URL}/${process.env.KEYCLOAK_REALM}/protocol/openid-connect/token`,
    new URLSearchParams({
      grant_type: "password",
      client_id: `${process.env.KEYCLOAK_CLIENT_ID}`,
      scope: "openid",
      username: `${process.env.PW_USERNAME}`,
      password: `${process.env.PW_PASSWORD}`,
    })
  );
  return token;
}

// TODO: remove after all instances removed
/**
 * Generic Function that receives the API token and perform graphql queries and mutations
 * @param  {APIRequestContext} request
 * @param  {string} tokenAPI
 * @param  {string} operationName
 * @param  {string} query
 * @param  {Record<string} variables?
 */
async function graphQLRequest(
  request: APIRequestContext,
  tokenAPI: string,
  operationName: string,
  query: string,
  variables?: Record<string, any>
): Promise<APIResponse> {
  const response = await request.post(process.env.API_BASEURL ?? "/", {
    headers: {
      Authorization: `Bearer ${tokenAPI}`,
    },
    data: {
      operationName,
      query,
      variables,
    },
  });
  return response;
}

async function graphQlAxiosRequest(
  tokenAPI: string,
  operationName: string,
  query: string,
  variables?: Record<string, any>
): Promise<CustomAxiosResponse> {
  const { data, status, statusText } = await axios({
    url: process.env.API_BASEURL ?? "/",
    method: "post",
    headers: {
      Authorization: `Bearer ${tokenAPI}`,
    },
    data: {
      operationName,
      query,
      variables,
    },
  });

  const isResponseOk = status >= 200 && status <= 299;

  return { status, statusText, ok: isResponseOk, ...data };
}

/**
 * Generic Function that perform graphql queries and mutations
 * The API token is being added to the HTTP request with extraHTTPHeaders
 *   under playwright.config.ts
 * The global-setup.ts is responsible to get the token value using axios
 * @param  {APIRequestContext} request
 * @param  {string} operationName
 * @param  {string} query
 * @param  {Record<string} variables?
 */
async function graphQLRequestNoHeader(
  request: APIRequestContext,
  operationName: string,
  query: string,
  variables?: Record<string, any>
): Promise<APIResponse> {
  const response = await request.post(process.env.API_BASEURL ?? "/", {
    data: {
      operationName,
      query,
      variables,
    },
  });
  return response;
}

type GenericObject = Record<string, string>;
/**
 * Function that receives queries data output and returns a requested prop
 * @param  {Record<string} data
 */
const extractProp = (data: GenericObject | GenericObject[], prop: string) =>
  (Array.isArray(data) ? data : [data])
    .map(entry => entry[prop] ?? null)
    .filter(entry => !!entry);

export {
  extractProp,
  graphQLRequest,
  graphQlAxiosRequest,
  graphQLRequestNoHeader,
  getAPIAccessToken,
};
