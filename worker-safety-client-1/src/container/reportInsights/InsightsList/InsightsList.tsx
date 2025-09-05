import type { Insight } from "@/types/insights/Insight";
import InsightsListItem from "./InsightsListItem";

interface InsightsListProps {
  insights: Insight[];
  changeActiveInsight: (id: string) => void;
  activeInsightId: string;
}

const InsightsList = ({
  insights,
  changeActiveInsight,
  activeInsightId,
}: InsightsListProps) => {
  return (
    <>
      {insights.map(insight => (
        <InsightsListItem
          name={insight.name}
          isActive={insight.id === activeInsightId}
          key={insight.id}
          onClick={() => changeActiveInsight(insight.id)}
        />
      ))}
    </>
  );
};

export default InsightsList;
