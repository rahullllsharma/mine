type EmptyContentProps = {
  title: string;
  description: string;
};

export default function EmptyContent({
  title,
  description,
}: EmptyContentProps): JSX.Element {
  return (
    <div className="flex flex-col items-center w-full text-center px-6">
      <p className="text-neutral-shade-100 text-xl font-semibold mb-2">
        {title}
      </p>
      <p className="text-brand-gray-70 text-sm max-w-md">{description}</p>
    </div>
  );
}
