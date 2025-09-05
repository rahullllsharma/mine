import React, { ReactNode } from "react";
import style from "./cardStyle.module.scss";

interface CardProps {
  className: string;
  children: ReactNode;
  boxShadow?: boolean;
  defaultStyles?: boolean;
  customBoxShadow?: string;
}

const Card = ({
  children,
  className,
  boxShadow,
  defaultStyles = true,
  customBoxShadow,
}: CardProps) => {
  const cardClasses = [
    className,
    defaultStyles ? style.defaultCard : "",
    boxShadow && customBoxShadow ? customBoxShadow : "",
  ].join(" ");

  return <div className={cardClasses}>{children}</div>;
};

export default Card;
