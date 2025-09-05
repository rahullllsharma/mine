import { messages } from "@/locales/messages";

export default function EmptyIncidents() {
  return (
    <div className="text-center py-6">
      <div className="mb-1 text-xl font-semibold">
        {messages.historicIncidentEmptyTitle}
      </div>
      <div className="mb-8 text-neutral-shade-75">
        {messages.historicIncidentEmptyDescription}
      </div>
      <div className="font-semibold">
        {messages.historicIncidentEmptyExamples}
      </div>
    </div>
  );
}
