import { BodyText, SectionHeading } from "@urbint/silica";

// Convert snake_case to Title Case (e.g., "this_incident" -> "This incident")
export const formatSnakeCaseToTitleCase = (input: string): string => {
  if (!input) return "";

  return input
    .split("_")
    .map((word, index) => {
      if (index === 0) {
        // Capitalize first word
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
      } else {
        // Keep other words lowercase
        return word.toLowerCase();
      }
    })
    .join(" ");
};

// Check if incidents array is empty and return appropriate JSX
export const renderEmptyIncidents = (label: string) => {
  return (
    <div className="mt-6 p-4 bg-gray-100 rounded-md">
      <SectionHeading className="mb-3">{label}</SectionHeading>
      <BodyText className="text-sm text-gray-600">
        No content available for this job.
      </BodyText>
    </div>
  );
};
