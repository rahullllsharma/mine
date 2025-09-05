import type { Insight } from "@/types/insights/Insight";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

const PowerBIEmbed = dynamic(
  async () => (await import("powerbi-client-react")).PowerBIEmbed,
  {
    ssr: false,
  }
);

interface EmbeddedReportProps {
  insight: Insight;
  embedData: {
    embedUrl: string;
    reportId: string;
    id: string;
  };
  embedToken: string;
}

const EmbeddedReport = ({ embedData, embedToken }: EmbeddedReportProps) => {
  const [models, setModels] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const getModels = async () => {
      const modelsImport = (await import("powerbi-client")).models;
      return modelsImport;
    };

    getModels()
      .then(modelsImport => setModels(modelsImport))
      .catch(error => console.error(error));
  }, []);

  return models ? (
    <PowerBIEmbed
      embedConfig={{
        type: "report",
        id: embedData.reportId,
        embedUrl: embedData.embedUrl,
        accessToken: embedToken,
        tokenType: (models.TokenType as { Embed: 1 }).Embed,
      }}
      cssClassName="h-full"
      getEmbeddedComponent={component => {
        if (component) {
          component.iframe.style.height = "100%";
        }
      }}
    />
  ) : null;
};

export default EmbeddedReport;
