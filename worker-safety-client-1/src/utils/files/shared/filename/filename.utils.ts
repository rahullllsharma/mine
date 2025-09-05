import { convertToDate, getFormattedDate } from "@/utils/date/helper";

type GenerateExportedPortfolioFilenameArgs = {
  tenant: string;
  title: string;
  options?: GenerateExportUrbintSignatureOptions;
};
type GenerateExportUrbintSignatureOptions = {
  delimiter?: "/" | "_";
};
type GenerateExportedProjectFilenameArgs = {
  title: string;
  project: {
    number?: string;
    name: string;
  };
  options?: GenerateExportUrbintSignatureOptions;
};

/** Generate the urbint signature for the suffix filename */
const generateUrbintSignature = ({ delimiter = "/" } = {}) =>
  `Urbint-${getFormattedDate(
    convertToDate(),
    "2-digit",
    "2-digit",
    "2-digit"
  )}`.replaceAll("/", delimiter);

/** Generates a filename for a Project without the extension */
const generateExportedProjectFilename = ({
  title,
  project,
  options = {},
}: GenerateExportedProjectFilenameArgs): string => {
  return [
    project?.number ? `[${project?.number}]` : undefined,
    project.name,
    title,
    generateUrbintSignature(options),
  ]
    .filter(Boolean)
    .join("-");
};

/** Generates a filename for a Project without the extension */
const generateExportedPortfolioFilename = ({
  tenant,
  title,
  options = {},
}: GenerateExportedPortfolioFilenameArgs): string => {
  return [tenant, title, generateUrbintSignature(options)].join("-");
};

export { generateExportedPortfolioFilename, generateExportedProjectFilename };
