import type { PropsWithChildren } from "react";
import { Droppable } from "react-beautiful-dnd";

const DroppableTableBody = ({
  children,
  ...otherProps
}: PropsWithChildren<Record<string, unknown>>): JSX.Element => {
  return (
    <Droppable droppableId="table-body">
      {({ droppableProps, placeholder, innerRef }) => (
        <div {...droppableProps} ref={innerRef} {...otherProps}>
          {children}
          {placeholder}
        </div>
      )}
    </Droppable>
  );
};

export default DroppableTableBody;
