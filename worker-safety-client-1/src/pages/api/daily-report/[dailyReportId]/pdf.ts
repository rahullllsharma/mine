import type { GetServerSidePropsContext } from "next";
import { authenticatedQuery } from "@/graphql/client";
import getDailyReportWithLocationProject from "@/graphql/queries/dailyReport/getDailyReportWithLocationProject.gql";
import { stripTypename } from "@/utils/shared";
import { generateDailyReportPDF } from "@/server/dailyReport/services/pdf";
import { canDownloadReports } from "@/container/report/dailyInspection/permissions";
import { withAuthMiddleware } from "@/hooks/auth/middleware/withAuthMiddleware";
import { withPermissionsMiddleware } from "@/hooks/auth/middleware/withPermissionsMiddleware";

/** Acts as a Controller and (will) manage the PDF generation for a given valid daily report. */
const handler: UrbintNextApiHandler = async (req, res) => {
  try {
    const { user } = req.locals;

    const { dailyReportId: id } = req.query;

    const { data } = await authenticatedQuery(
      {
        query: getDailyReportWithLocationProject,
        variables: {
          id,
        },
      },
      {
        req,
        res,
      } as unknown as GetServerSidePropsContext
    );

    const { dailyReport } = stripTypename(data);

    // skip when the UUID passed, doesn't find a daily report
    if (data?.dailyReport === null) {
      res.status(404);
      return res.send("");
    }

    // If the user doesn't have permissions to access the daily report, reject it.
    if (!canDownloadReports(user)) {
      res.status(403);
      return res.send("");
    }

    const pdf = await generateDailyReportPDF({
      data: {
        dailyReport,
        user,
      },
    });

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Length", pdf.length);

    return res.send(pdf);
  } catch (err) {
    res.status(500);
    return res.send("");
  }
};

export default withAuthMiddleware(withPermissionsMiddleware(handler));
