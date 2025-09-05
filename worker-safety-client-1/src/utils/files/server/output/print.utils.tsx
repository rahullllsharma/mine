import { renderToStaticMarkup } from "react-dom/server";
import { PrintTemplate } from "./templates/PrintTemplate";

type GeneratePrintFromTemplateProps<T> = {
  template: (props: T) => JSX.Element;
  data: T;
};

function generatePrintFromTemplate<T>({
  template: Template,
  data,
}: GeneratePrintFromTemplateProps<T>): string {
  return renderToStaticMarkup(
    <PrintTemplate>
      <Template {...data} />
    </PrintTemplate>
  );
}

export { generatePrintFromTemplate };
