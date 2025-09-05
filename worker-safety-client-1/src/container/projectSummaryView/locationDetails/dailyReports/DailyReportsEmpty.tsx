import { useAuthStore } from "@/store/auth/useAuthStore.store";
import EmptySection from "../EmptySection";

export default function DailyReportsEmpty(
  onDailyReportClick: () => void
): JSX.Element {
  const { hasPermission } = useAuthStore();
  return (
    <EmptySection
      text="No daily inspection reports have been added today"
      buttonLabel="Add a report"
      onClick={hasPermission("ADD_REPORTS") ? onDailyReportClick : undefined}
    />
  );
}
