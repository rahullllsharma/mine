import puppeteer from "puppeteer-core";

type GeneratePdfOptions = { headerTemplate?: string; footerTemplate?: string };
type GeneratePdfFunction = (
  content: string,
  options: GeneratePdfOptions
) => Promise<Buffer>;

/** General page margins */
const pageMargin = 16;

/** Generate a PDF buffer from a html/string context */
const generatePDF: GeneratePdfFunction = async (
  content: string,
  { headerTemplate, footerTemplate }
) => {
  if (!process.env.PUPPETEER_EXECUTABLE_PATH) {
    throw new Error("Missing Chrome binary");
  }

  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ["--no-sandbox", "--headless", "--disable-gpu"],
  });

  const page = await browser.newPage();

  await page.setContent(content, {
    waitUntil: "domcontentloaded",
  });

  // wait for fonts to be loaded.
  await page.evaluateHandle("document.fonts.ready");

  const pdfBuffer = await page.pdf({
    displayHeaderFooter: Boolean(headerTemplate || footerTemplate),
    headerTemplate,
    footerTemplate,
    format: "A4",
    margin: {
      left: pageMargin,
      right: pageMargin,
      // Magic number: creates space for header plus padding
      top: headerTemplate ? 90 : pageMargin,
      // Magic number: creates space for the footer
      bottom: footerTemplate ? 50 : pageMargin,
    },
    printBackground: true,
  });

  await browser.close();

  return pdfBuffer;
};

export { generatePDF };
