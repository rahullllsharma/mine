export type SectionItem = {
  title: string;
  description?: string | string[];
};

type ProjectPrintSectionProps = {
  header: string;
  items: SectionItem[];
};

const getDescription = (description?: string | string[]): string => {
  if (!description || description.length === 0) return "-";

  return Array.isArray(description) ? description.join(", ") : description;
};

const SectionHeader = ({ title }: Pick<SectionItem, "title">): JSX.Element => (
  <h5 className="py-1 px-4 text-base bg-brand-gray-10 border-t border-b border-brand-gray-40">
    <span className="text-neutral-shade-100 font-semibold">{title}</span>
  </h5>
);

const SectionRow = ({ title, description }: SectionItem): JSX.Element => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 border-b border-neutral-shade-26 text-neutral-shade-100 text-base">
      <span className="px-4 py-1 w-42 font-semibold">{title}</span>
      <span className="px-4 py-1 border-l border-neutral-shade-26 col-span-1 sm:col-span-2">
        {getDescription(description)}
      </span>
    </div>
  );
};

export default function ProjectPrintSection({
  header,
  items,
}: ProjectPrintSectionProps): JSX.Element {
  return (
    <div>
      <SectionHeader title={header} />
      {items.map((item, index) => (
        <SectionRow
          key={index}
          title={item.title}
          description={item.description}
        />
      ))}
    </div>
  );
}
