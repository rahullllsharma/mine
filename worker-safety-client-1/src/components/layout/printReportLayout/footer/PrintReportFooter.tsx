type PrintReportFooterProps = {
  note?: string;
};

/**
 * Footer component for the Daily Report PDF.
 *
 * Since this is passed as a html string, it doesn't inherit any styling properties from the inner document like styles nor custom fonts.
 * Thus we need to set everything (font-size, font-family, etc) and avoid having relative units like rem (em is ok tho).
 */
export default function PrintReportFooter({
  note,
}: PrintReportFooterProps): JSX.Element {
  return (
    <footer className="flex items-center text-neutral-shade-100 font-sans font-normal text-base px-[12px] w-full">
      {note && <p className="text-xs">{note}</p>}
      {/*
        pageNumber is a special class from puppeteer to display the page number.
        https://pptr.dev/api/puppeteer.pdfoptions.headertemplate/
      */}
      <p
        data-testid="print-report-footer-pagination"
        className="text-tiny ml-auto pageNumber"
      ></p>
    </footer>
  );
}
