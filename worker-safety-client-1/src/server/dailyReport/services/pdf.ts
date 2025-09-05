import type { DailyReportPrintTemplateProps } from "@/components/layout/printReportLayout/DailyReportPrintTemplate";

import { generatePrintFromTemplate, generatePDF } from "@/utils/files/server";
import { DailyReportPrintTemplate } from "@/components/layout/printReportLayout/DailyReportPrintTemplate";
import PrintReportHeader from "@/components/layout/printReportLayout/header/PrintReportHeader";
import PrintReportFooter from "@/components/layout/printReportLayout/footer/PrintReportFooter";
import { getGenerationDate } from "@/utils/date/helper";
import { renderComponentToHtmlStringInlineStyles } from "./renderComponentToString";

/** Parse the header and footer components to HTML with inline styles. */
const renderDailyReportHeaderAndFooter = async ({
  dailyReport,
  user,
}: DailyReportPrintTemplateProps) => {
  const { name, project } = dailyReport.location;
  const headerTemplate = await renderComponentToHtmlStringInlineStyles(
    PrintReportHeader,
    {
      subtitle: `${project.name} • ${name}`,
    }
  );

  const footerTemplate = await renderComponentToHtmlStringInlineStyles(
    PrintReportFooter,
    {
      note: `Generated on ${getGenerationDate()} by ${user.name}`,
    }
  );
  // compile both header and footer
  return { headerTemplate, footerTemplate };
};

/** Creates the PDF buffer content */
const generateDailyReportPDF = async ({
  data,
}: {
  data: DailyReportPrintTemplateProps;
}): Promise<Buffer> => {
  const output = generatePrintFromTemplate({
    template: DailyReportPrintTemplate,
    data,
  });

  const { headerTemplate, footerTemplate } =
    await renderDailyReportHeaderAndFooter(data);

  return generatePDF(output, {
    headerTemplate,
    footerTemplate,
  });
};

export { generateDailyReportPDF };
