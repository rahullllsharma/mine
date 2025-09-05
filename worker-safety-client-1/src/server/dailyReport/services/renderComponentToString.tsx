import type { ReactElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import inline from "inline-css";
import { config } from "@/config.server";

/**
 * Render a given component to HTML with the print styles injected inline.
 */
async function renderComponentToHtmlStringInlineStyles<T>(
  Component: (props: T) => ReactElement,
  props: T
): Promise<string | undefined> {
  const componentAsPureMarkup = renderToStaticMarkup(<Component {...props} />);

  try {
    const componentWithInlineStyles = await inline(componentAsPureMarkup, {
      extraCss: config.workerSafetyPrintStylesheet,
      url: config.workerSafetyPrintStylesheet,
      // this needs to be false otherwise it could remove classes necessary for puppeteer
      removeHtmlSelectors: false,
    });

    // The inline-css library adds the whole body - html>head+body>component
    // Thus we just need the element INSIDE the body element
    const groups = componentWithInlineStyles.match(
      /<body[^>]*>([^<]*(?:(?!<\/?body)<[^<]*)*)<\/body\s*>/i
    );

    if (groups?.length !== 2) {
      throw new Error(`Element not found inside! ${componentWithInlineStyles}`);
    }

    return groups[1];
  } catch (err) {
    console.error("something went very bad", err);
  }
}

export { renderComponentToHtmlStringInlineStyles };
