import Link from "@/components/shared/link/Link";

type WorkProcedureLinksProps = {
  id: string;
};

export function WorkProcedureLinks({ id }: WorkProcedureLinksProps) {
  switch (id) {
    case "distribution_bulletins":
      return (
        <Link
          label="Distribution Bulletins"
          iconRight="external_link"
          href="https://mobi.southernco.com/D_Bulletins/home"
          target="_blank"
          className="gap-2 flex items-center w-full md:w-auto"
        />
      );
    case "four_rules_of_cover_up":
      return (
        <Link
          label="Additional documentation"
          iconRight="external_link"
          href="https://soco365.sharepoint.com/:b:/r/sites/GPCSafetyandHealthALL/Shared Documents/General/eJSB/4 RULES OF COVER UP.pdf?csf=1&web=1&e=XZR0v1"
          target="_blank"
          className="gap-2 flex items-center w-full md:w-auto"
        />
      );
    case "sdop_switching_procedures":
      return (
        <Link
          label="Switching Procedures"
          iconRight="external_link"
          href="https://soco365.sharepoint.com/sites/intra_GPC_Power_Delivery/_layouts/15/viewer.aspx?sourcedoc={fed21851-6fba-4102-b4b0-69f64e987f8d}"
          target="_blank"
          className="gap-2 flex items-center w-full md:w-auto"
        />
      );
    case "toc":
      return (
        <Link
          label="TOC Request Form"
          iconRight="external_link"
          href="https://mobi.southernco.com/DCC_TOC_REQUEST/TOC"
          target="_blank"
          className="gap-2 flex items-center w-full md:w-auto"
        />
      );
    case "best_work_practices":
      return (
        <Link
          label="Best Work Practices"
          iconRight="external_link"
          href="https://soco365.sharepoint.com/sites/intra_GPC_Safety_and_Health/SitePages/Best-Work-Practices.aspx"
          target="_blank"
          className="gap-2 flex items-center w-full md:w-auto"
        />
      );

    default:
      return null;
  }
}
