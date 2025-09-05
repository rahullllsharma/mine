import type { PropsWithChildren } from "react";
import type { DragDropContextProps } from "react-beautiful-dnd";
import { DragDropContext } from "react-beautiful-dnd";

interface DragDropContextComponentProps
  extends Pick<DragDropContextProps, "onDragEnd">,
    Record<string, unknown> {}

const DragDropContextComponent = ({
  children,
  onDragEnd,
  ...otherProps
}: PropsWithChildren<DragDropContextComponentProps>): JSX.Element => {
  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div {...otherProps}>{children}</div>
    </DragDropContext>
  );
};

export default DragDropContextComponent;
