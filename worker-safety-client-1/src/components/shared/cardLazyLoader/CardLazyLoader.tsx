import React from "react";
import cx from "classnames";

interface CardLazyLoaderProps {
  className?: string;
  cards?: number;
  rowsPerCard?: number;
  rowClassName?: string;
}

const CardLazyLoader: React.FC<CardLazyLoaderProps> = ({
  className = "",
  cards = 2,
  rowsPerCard = 1,
  rowClassName = "",
}) => {
  const cardElements = Array.from({ length: cards }).map((_card, cardIndex) => (
    <div
      key={cardIndex}
      className="mb-4 mt-5 bg-gray-100 rounded p-3 min-h-[8rem]"
    >
      <div className="flex items-center space-x-4">
        <div className="flex-1 space-y-2">
          <div className="h-5 bg-gray-300 rounded w-1/4"></div>
          {Array.from({ length: rowsPerCard }).map((_row, rowIndex) => (
            <div
              key={rowIndex}
              className={cx("h-12 bg-gray-300 rounded w-auto", rowClassName)}
            ></div>
          ))}
        </div>
      </div>
    </div>
  ));

  return <div className={cx("animate-pulse", className)}>{cardElements}</div>;
};

export default CardLazyLoader;
