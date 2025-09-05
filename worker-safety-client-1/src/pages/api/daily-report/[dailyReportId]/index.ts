import type { GetServerSidePropsContext } from "next";
import stream from "stream";
import JSZip from "jszip";
import { authenticatedQuery } from "@/graphql/client";
import getDailyReportWithLocationProject from "@/graphql/queries/dailyReport/getDailyReportWithLocationProject.gql";
import { stripTypename } from "@/utils/shared";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { getDailyReportAttachments } from "@/server/dailyReport/services/attachments";
import { generateDailyReportPDF } from "@/server/dailyReport/services/pdf";
import { canDownloadReports } from "@/container/report/dailyInspection/permissions";
import { withPermissionsMiddleware } from "@/hooks/auth/middleware/withPermissionsMiddleware";
import { withAuthMiddleware } from "@/hooks/auth/middleware/withAuthMiddleware";

/** Acts as a Controller and (will) manage the PDF generation with attachments for a given valid daily report. */
const handler: UrbintNextApiHandler = async (req, res) => {
  console.time("[DIR] :: -> Generate zip file and download file");
  console.timeLog("[DIR] :: -> Generate zip file and download file");
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

    // Preparing additional information for creating the PDF and downloading the attachments async.
    const {
      sections,
      location: {
        project: { name: projectName, number: projectNumber },
      },
    } = dailyReport;

    // Finally generate the zip and pdf name
    const filename = generateExportedProjectFilename({
      title: "Daily Inspection Report Export",
      project: { name: projectName, number: projectNumber },
      options: {
        delimiter: "_",
      },
    });

    const results = await generateDailyReportPDF({
      data: {
        dailyReport,
        user,
      },
    });

    const attachments = await getDailyReportAttachments(sections);
    console.timeEnd("[DIR] :: << Fetch Attachments");

    res.setHeader("Content-Type", "application/octet-stream");
    res.setHeader("Content-Transfer-Encoding", "Binary");
    res.setHeader(
      "Content-Disposition",
      `"attachment; filename=${filename}.zip"`
    );
    res.setHeader("Connection", "Keep-Alive");
    res.setHeader("Keep-Alive", "timeout=5");
    res.setHeader("Transfer-Encoding", "chunked");

    // Generate the zip object
    const jszip = new JSZip();
    [
      {
        content: results,
        file: `${filename}.pdf`,
      },
      ...attachments,
    ].forEach(({ file: currentFileName, content }) => {
      jszip.file(currentFileName, content, {
        binary: true,
      });
    });

    return jszip
      .generateInternalStream({
        streamFiles: true,
        type: "nodebuffer",
        compression: "DEFLATE",
        compressionOptions: { level: 9 },
      })
      .accumulate()
      .then(result => {
        const readStream = new stream.PassThrough();
        readStream.end(result);
        readStream.pipe(res);

        /// FIXME: write to GCP
      })
      .catch(err => {
        console.log(err);
        console.log("[DIR] :: << FAILED Generate zip file and download file");
      })
      .finally(() => {
        console.timeEnd("[DIR] :: -> Generate zip file and download file");
      });
  } catch (err) {
    res.status(500);
    return res.send("");
  }
};

export default withAuthMiddleware(withPermissionsMiddleware(handler));

export const config = {
  api: {
    responseLimit: false,
  },
};
