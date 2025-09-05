import type { Page, APIRequestContext } from "@playwright/test";
import { expect } from "../../framework/base-fixtures";
import { graphQLRequestNoHeader } from "../../framework/graphql-client";
import { BasePage } from "../base-page";

export class BaseAPIPage extends BasePage {
  readonly request: APIRequestContext;
  tokenAPI: string;

  constructor(page: Page, request: APIRequestContext) {
    super(page);
    this.request = request;
  }

  /**
   * Function that calls graphQLRequestNoHeader with extended test request (this.request) object
   */
  async graphQLReqWithTestReq(
    operationName: string,
    query: string,
    variables?: Record<string, any>
  ) {
    const response = await graphQLRequestNoHeader(
      this.request,
      operationName,
      query,
      variables
    );
    expect(response.ok()).toBeTruthy();
    return response;
  }
}
