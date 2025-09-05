export type TableLoaderProps = {
  columnsSize: number;
  rows?: number;
};

function TableRow({ columnsSize }: { columnsSize: number }) {
  const placeholderClasses = "h-5 rounded animate-pulse block";
  const darkGray = "bg-gray-300";
  const lightGray = "bg-gray-200";
  return (
    <div
      className="_tr flex w-max px-4 bg-white min-h-[3.5rem] items-center"
      style={{
        top: 0,
        left: 0,
        minWidth: "100%",
      }}
      role="row"
    >
      {[...Array(columnsSize)].map((key, index) => {
        const grayType = index % 2 === 0 ? darkGray : lightGray;
        return (
          <div className="_td flex-grow" key={index}>
            <span className={`w-32 ${placeholderClasses} ${grayType}`} />
          </div>
        );
      })}
    </div>
  );
}

function TableLoader({
  columnsSize,
  rows = 10, // max limit is 50
}: TableLoaderProps): JSX.Element {
  return (
    <>
      {[...Array(Math.abs(rows) > 50 ? 50 : rows)].map((_, key) => (
        <TableRow key={key} columnsSize={columnsSize} />
      ))}
    </>
  );
}

export { TableLoader };
