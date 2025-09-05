import type { PropsWithChildren } from "react";
import { Icon } from "@urbint/silica";
import { Draggable } from "react-beautiful-dnd";

interface DraggableTableRowProps extends Record<string, unknown> {
  index: number;
  id: string;
}

const DraggableTableRow = ({
  id,
  index,
  children,
  ...otherProps
}: PropsWithChildren<DraggableTableRowProps>): JSX.Element => {
  return (
    <Draggable draggableId={id} index={index}>
      {({ draggableProps, innerRef, dragHandleProps }) => (
        <div {...otherProps} {...draggableProps} ref={innerRef}>
          <div
            className="w-0 -ml-0.5 flex justify-start text-gray-400"
            {...dragHandleProps}
          >
            <Icon name="grid_vertical_round" />
          </div>
          {children}
        </div>
      )}
    </Draggable>
  );
};

export default DraggableTableRow;
