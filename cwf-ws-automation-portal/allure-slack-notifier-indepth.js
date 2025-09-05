const fs = require("fs");
const path = require("path");
const { WebClient } = require("@slack/web-api");
const dotenv = require("dotenv");
dotenv.config();

const SLACK_TOKEN = process.env.SLACK_BOT_TOKEN;
const SLACK_CHANNEL = process.env.SLACK_CHANNEL_ID;
const ALLURE_RESULTS_DIR = "./allure-results";
const ALLURE_REPORT_PATH = "./allure-report/index.html";
const TS_ENV_CONFIG_PATH = "./Data/envConfig.ts";
const TS_TENANT_CONFIG_PATH = "./Data/tenantConfig.ts";

const slackClient = new WebClient(SLACK_TOKEN);

function getCurrentEnvFromTSConfig(tsFilePath) {
  const fileContent = fs.readFileSync(tsFilePath, "utf8");
  const match = fileContent.match(
    /export\s+const\s+CURRENT_ENV[^=]*=\s*["'`](\w+)["'`]/
  );
  if (match) {
    return match[1];
  }
  return "unknown";
}

function getCurrentTenantFromTSConfig(tsFilePath) {
  const fileContent = fs.readFileSync(tsFilePath, "utf8");
  const match = fileContent.match(/CURRENT_TENANT:\s*["'`]([^"'`]+)["'`]/);
  if (match) {
    return match[1];
  }
  return "unknown";
}

function extractTenantFromUrl(url) {
  if (!url) return "unknown";

  try {
    // Handle different URL formats:
    // https://{tenant}.ws.{environment}.urbinternal.com/
    // https://{tenant}.ws.urbint.com/
    // https://{tenant}-{environment}.urbinternal.com/
    const urlObj = new URL(url);
    const hostname = urlObj.hostname;

    // Extract tenant from hostname
    const parts = hostname.split(".");
    if (parts.length >= 3) {
      // Format: tenant.ws.environment.urbinternal.com or tenant.ws.urbint.com
      const firstPart = parts[0];
      if (firstPart && firstPart !== "www") {
        return firstPart;
      }
    } else if (parts.length >= 2) {
      // Format: tenant-environment.urbinternal.com
      const firstPart = parts[0];
      if (firstPart && firstPart !== "www") {
        // Extract tenant part before the dash
        const tenantPart = firstPart.split("-")[0];
        if (tenantPart) {
          return tenantPart;
        }
      }
    }
  } catch (error) {
    console.warn(
      "Could not parse URL for tenant extraction:",
      url,
      error.message
    );
  }

  return "unknown";
}

function getTenantFromEnvironment() {
  // First try to get tenant from config file
  const configTenant = getCurrentTenantFromTSConfig(TS_TENANT_CONFIG_PATH);
  if (configTenant && configTenant !== "unknown") {
    return configTenant;
  }

  // If not found in config, try to extract from environment variables
  const envUrl =
    process.env.STAGING_URL || process.env.INTEG_URL || process.env.PROD_URL;
  if (envUrl) {
    const extractedTenant = extractTenantFromUrl(envUrl);
    return extractedTenant;
  }

  return "unknown";
}

const CURRENT_ENV = getCurrentEnvFromTSConfig(TS_ENV_CONFIG_PATH);
const CURRENT_TENANT = getTenantFromEnvironment();

function parseAllureResultsByProject() {
  const resultsDir = fs.readdirSync(ALLURE_RESULTS_DIR);
  const allResults = [];

  // Collect all results
  resultsDir.forEach((file) => {
    if (file.endsWith("-result.json")) {
      const resultPath = path.join(ALLURE_RESULTS_DIR, file);
      const testResult = JSON.parse(fs.readFileSync(resultPath, "utf8"));
      allResults.push(testResult);
    }
  });

  // Deduplicate by historyId, prefer passed > failed > broken > skipped
  const resultByHistoryId = {};
  allResults.forEach((result) => {
    const hid = result.historyId;
    if (!hid) return;
    if (!resultByHistoryId[hid]) {
      resultByHistoryId[hid] = result;
    } else {
      // Prefer passed > failed > broken > skipped
      const statusPriority = { passed: 3, failed: 2, broken: 1, skipped: 0 };
      if (
        statusPriority[result.status] >
        statusPriority[resultByHistoryId[hid].status]
      ) {
        resultByHistoryId[hid] = result;
      }
    }
  });

  // Now aggregate by project
  const projectResults = {};
  Object.values(resultByHistoryId).forEach((testResult) => {
    // Find the project label, fallback to parentSuite if not present
    let project = "unknown";
    const labels = testResult.labels || [];
    const projectLabel = labels.find((l) => l.name === "project");
    if (projectLabel) {
      project = projectLabel.value;
    } else {
      const parentSuiteLabel = labels.find((l) => l.name === "parentSuite");
      if (parentSuiteLabel) {
        project = parentSuiteLabel.value;
      }
    }

    if (!projectResults[project]) {
      projectResults[project] = {
        passed: 0,
        failed: 0,
        skipped: 0,
        broken: 0,
        total: 0,
        failureDetails: [],
      };
    }

    switch (testResult.status) {
      case "passed":
        projectResults[project].passed++;
        break;
      case "failed":
        projectResults[project].failed++;
        projectResults[project].failureDetails.push({
          name: testResult.name || "Unnamed test",
        });
        break;
      case "skipped":
        projectResults[project].skipped++;
        break;
      case "broken":
        projectResults[project].broken++;
        projectResults[project].failureDetails.push({
          name: testResult.name || "Unnamed test",
        });
        break;
    }
    projectResults[project].total++;
  });

  // Calculate pass rate for each project
  for (const project in projectResults) {
    const { passed, failed, broken } = projectResults[project];
    const executed = passed + failed + broken;
    projectResults[project].passRate =
      executed > 0 ? ((passed / executed) * 100).toFixed(2) : "0.00";
  }

  return projectResults;
}

function formatFailureDetails(failureDetails) {
  if (failureDetails.length === 0) {
    return "";
  }

  let text = "*Failed Tests Details:*\n\n";

  failureDetails.forEach((failure, index) => {
    if (index < 5) {
      text += `*${index + 1}. ${failure.name}*\n`;
      // No error message or trace
      text += `\n`;
    } else if (index === 5) {
      text += `_...and ${failureDetails.length - 5} more failed tests._\n`;
    }
  });

  return text;
}

async function sendSlackNotification() {
  try {
    if (!fs.existsSync(ALLURE_REPORT_PATH)) {
      console.warn(`Warning: HTML report not found at: ${ALLURE_REPORT_PATH}`);
    }

    // Use the new parser
    const projectResults = parseAllureResultsByProject();
    const timestamp = new Date().toLocaleString();

    // Find suite name from Allure results
    let suiteName = null;
    const resultsDir = fs.readdirSync(ALLURE_RESULTS_DIR);
    const suiteNames = new Set();
    resultsDir.forEach((file) => {
      if (file.endsWith("-result.json")) {
        const resultPath = path.join(ALLURE_RESULTS_DIR, file);
        const testResult = JSON.parse(fs.readFileSync(resultPath, "utf8"));
        const labels = testResult.labels || [];
        // Prefer 'suite', fallback to 'package'
        let suiteLabel = labels.find((l) => l.name === "suite");
        if (!suiteLabel) suiteLabel = labels.find((l) => l.name === "package");
        if (suiteLabel) suiteNames.add(suiteLabel.value);
      }
    });
    if (suiteNames.size === 1) {
      suiteName = Array.from(suiteNames)[0];
    } else if (suiteNames.size > 1) {
      suiteName = "Multiple Suites";
    } else {
      suiteName = "Unknown Suite";
    }

    // Calculate overall pass rate (excluding skipped)
    let totalPassed = 0,
      totalFailed = 0,
      totalBroken = 0;
    for (const metrics of Object.values(projectResults)) {
      totalPassed += metrics.passed;
      totalFailed += metrics.failed;
      totalBroken += metrics.broken;
    }
    const totalExecuted = totalPassed + totalFailed + totalBroken;
    const overallPassRate =
      totalExecuted > 0
        ? ((totalPassed / totalExecuted) * 100).toFixed(2)
        : "0.00";

    const blocks = [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `Test Results - ${suiteName} - ${CURRENT_ENV} env and ${CURRENT_TENANT} tenant - (Overall Pass Rate: ${overallPassRate}%)`,
          emoji: true,
        },
      },
    ];

    for (const [project, metrics] of Object.entries(projectResults)) {
      let statusEmoji = " ✅ ";
      if (metrics.failed > 0 || metrics.broken > 0) {
        statusEmoji = " ❌ ";
      } else if (metrics.skipped > 0 && metrics.passed === 0) {
        statusEmoji = " ⚠️ ";
      } else if (metrics.skipped > 0) {
        statusEmoji = " ✅⏩ ";
      }

      blocks.push({
        type: "section",
        text: {
          type: "mrkdwn",
          text: `${statusEmoji} *${metrics.passRate}%* - *${project}* + \`${CURRENT_ENV}\` Env and \`${CURRENT_TENANT}\` Tenant\n• Total: \`${metrics.total}\`  ✅\`${metrics.passed}\` ❌\`${metrics.failed}\` ⏭️\`${metrics.skipped}\``,
        },
      });

      // Optionally, add failure details per project
      if (metrics.failureDetails.length > 0) {
        blocks.push({ type: "divider" });
        blocks.push({
          type: "section",
          text: {
            type: "mrkdwn",
            text: formatFailureDetails(metrics.failureDetails),
          },
        });
      }
    }

    blocks.push({
      type: "context",
      elements: [
        {
          type: "mrkdwn",
          text: `Report generated at ${timestamp}`,
        },
      ],
    });

    const message = {
      channel: SLACK_CHANNEL,
      text: `Test Results - ${suiteName} - ${CURRENT_ENV} env and ${CURRENT_TENANT} tenant - (Overall Pass Rate: ${overallPassRate}%)`,
      blocks: blocks,
    };

    await slackClient.chat.postMessage(message);

    if (fs.existsSync(ALLURE_REPORT_PATH)) {
      // Use local time for the filename and title
      const pad = (n) => n.toString().padStart(2, "0");
      const now = new Date();
      const formattedDate = `${now.getFullYear()}-${pad(
        now.getMonth() + 1
      )}-${pad(now.getDate())}_${pad(now.getHours())}:${pad(
        now.getMinutes()
      )}:${pad(now.getSeconds())}`;
      const reportFilename = `${formattedDate}_allure_report.html`;
      await slackClient.files.uploadV2({
        channel_id: SLACK_CHANNEL,
        file: fs.createReadStream(ALLURE_REPORT_PATH),
        filename: reportFilename,
        title: `Allure Test Report - ${CURRENT_ENV} env and ${CURRENT_TENANT} tenant - ${formattedDate}`,
        initial_comment: `Complete HTML report from the latest test run - ${CURRENT_ENV} environment and ${CURRENT_TENANT} tenant`,
      });
    }
  } catch (error) {
    console.error("Error sending Slack notification:", error);
  }
}

// Main execution
sendSlackNotification();
