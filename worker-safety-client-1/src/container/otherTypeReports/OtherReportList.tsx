import InsightsListItem from "../reportInsights/InsightsList/InsightsListItem";

type OtherReportListProps = {
  reports: OtherReportType[];
  changeActiveReport: (id: string) => void;
  activeReportId: string;
};
type OtherReportType = {
  name: string;
  path: string;
  id: string;
  isEnable: boolean;
};

function OtherReportList({
  reports,
  changeActiveReport,
  activeReportId,
}: OtherReportListProps) {
  return (
    <>
      {reports.map(report => (
        <InsightsListItem
          name={report.name}
          isActive={report.id === activeReportId}
          key={report.id}
          onClick={() => changeActiveReport(report.id)}
        />
      ))}
    </>
  );
}

export default OtherReportList;
