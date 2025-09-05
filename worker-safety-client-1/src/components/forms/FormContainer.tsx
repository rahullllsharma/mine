export type FormContainerProps = {
  children: React.ReactNode;
};
export function FormContainer({ children }: FormContainerProps): JSX.Element {
  return (
    <div className="flex flex-col gap-1 max-h-[80vh] overflow-y-auto">
      {children}
    </div>
  );
}
