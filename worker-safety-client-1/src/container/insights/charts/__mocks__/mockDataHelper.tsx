/* eslint-disable @typescript-eslint/no-explicit-any */
import type { MockedResponse } from "@apollo/client/testing";
import type { PropsWithChildren } from "react";
import { act, render } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { chartRenderHelper } from "@/utils/dev/jest";

export function InsightsMockedProvider({
  children,
  mocks,
}: PropsWithChildren<any> & { mocks: ReadonlyArray<MockedResponse> }): any {
  return (
    <MockedProvider mocks={mocks} addTypename>
      {children}
    </MockedProvider>
  );
}

export async function renderInsightsChart(
  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  children: any,
  mocks: MockedResponse[]
): Promise<HTMLElement> {
  const triggerResize = chartRenderHelper();
  const { container } = render(
    <InsightsMockedProvider mocks={mocks}>{children}</InsightsMockedProvider>
  );

  // mockedProvider requires a short wait while the event loop advances
  await act(async () => {
    await new Promise(res => setTimeout(res, 150));
  });

  // jest requires a resize to render the charts
  triggerResize();
  return container;
}
