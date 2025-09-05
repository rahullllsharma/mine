export default function StepLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <div className="flex flex-1 flex-col gap-5 w-screen md:w-full max-w-[760px]">
      {children}
    </div>
  );
}
