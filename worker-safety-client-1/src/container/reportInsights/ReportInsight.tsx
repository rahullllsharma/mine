import type { Insight } from "@/types/insights/Insight";
import { useRef } from "react";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import useFullscreen from "@/hooks/useFullscreen";
import EmbeddedReport from "./EmbeddedReport";

interface ReportInsightProps {
  insight: Insight;
  embedData?: {
    embedUrl: string;
    reportId: string;
    id: string;
  };
  embedToken: string;
}

const ReportInsight = ({
  insight,
  embedData,
  embedToken,
}: ReportInsightProps) => {
  const reportSectionRef = useRef<HTMLDivElement>(null);

  const { toggle: enterFullscreen } = useFullscreen(reportSectionRef);

  return (
    <div className="flex flex-col h-full">
      <section className="relative mb-8 flex justify-center">
        <h5 className="text-center font-medium break-words max-w-[calc(100%-8rem)]">
          {insight.name}
        </h5>
        <ButtonIcon
          iconName="expand"
          className="absolute top-0 right-4"
          onClick={enterFullscreen}
        />
      </section>
      <section className="flex-1" id="report-insight" ref={reportSectionRef}>
        {(() => {
          if (!embedData) {
            return (
              <iframe
                title="JSB_SelectedSiteConditions"
                width="100%"
                height="100%"
                src={insight.url}
                allowFullScreen={true}
              />
            );
          }

          if (embedData) {
            return (
              <EmbeddedReport
                insight={insight}
                embedData={embedData}
                embedToken={embedToken}
              />
            );
          }

          return <p>Some error occurred</p>;
        })()}
      </section>
    </div>
  );
};

export default ReportInsight;
