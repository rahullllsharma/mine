import { useState } from "react";

export type TruncatedTextProps = {
  text: string;
  maxCharacters?: number;
  className?: string;
  showEllipsis?: boolean;
};

const TruncatedText = ({
  text,
  className,
  maxCharacters = 100,
  showEllipsis = false,
}: TruncatedTextProps) => {
  const [isTruncated, setIsTruncated] = useState(text.length > maxCharacters);

  const toggleTruncate = () => {
    setIsTruncated(!isTruncated);
  };

  const truncatedText = isTruncated
    ? `${text.slice(0, maxCharacters)}${showEllipsis && "..."}`
    : text;

  return (
    <div className={className}>
      <span>{truncatedText}</span>
      {text.length > maxCharacters && (
        <button
          className="text-sm font-bold text-brand-urbint-40 ml-1"
          onClick={toggleTruncate}
        >
          {isTruncated ? "Show More" : "Show Less"}
        </button>
      )}
    </div>
  );
};

export { TruncatedText };
