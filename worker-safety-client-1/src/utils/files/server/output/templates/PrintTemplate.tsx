import type { PropsWithChildren } from "react";
import { config } from "@/config.server";

function PrintTemplate({ children }: PropsWithChildren<unknown>): JSX.Element {
  return (
    <html lang="en-us">
      {/* eslint-disable-next-line @next/next/no-head-element */}
      <head>
        <style
          dangerouslySetInnerHTML={{
            __html: config.workerSafetyPrintStylesheet,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}

export { PrintTemplate };
