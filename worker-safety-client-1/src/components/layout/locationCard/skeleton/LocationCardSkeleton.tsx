import ContentLoader from "react-content-loader";
import colors from "tailwindcss/colors";

type LocationCardSkeletonProps = {
  boxWidth?: number;
  boxHeight?: number;
  animationSpeed?: number;
};

const LocationCardSkeleton = ({
  boxWidth = 269,
  boxHeight = 94,
  animationSpeed = 2,
}: LocationCardSkeletonProps) => {
  return (
    <ContentLoader
      speed={animationSpeed}
      width={boxWidth}
      height={boxHeight}
      viewBox={`0 0 ${boxWidth} ${boxHeight}`}
      foregroundColor={colors.gray[300]}
    >
      <rect x="0" y="0" rx="3" ry="3" width="66%" height="16" />
      <rect x="80%" y="0" rx="3" ry="3" width="20%" height="16" />
      <rect x="0" y="24" rx="3" ry="3" width="75%" height="16" />
      <rect x="0" y="48" rx="3" ry="3" width="20%" height="12" />

      <rect x="0" y="68" rx="3" ry="3" width="30%" height="12" />
      <rect x="33%" y="68" rx="3" ry="3" width="30%" height="12" />
      <rect x="66%" y="68" rx="3" ry="3" width="30%" height="12" />
    </ContentLoader>
  );
};

export { LocationCardSkeleton };
