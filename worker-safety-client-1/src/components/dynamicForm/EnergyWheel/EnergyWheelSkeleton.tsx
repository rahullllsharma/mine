import React from "react";

const EnergyWheelSkeleton = ({ totalSections = 10 }) => {
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const [containerSize, setContainerSize] = React.useState(480);

  React.useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        // Get the smaller dimension (width or height) to ensure wheel fits
        const container = containerRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight;
        const newSize = Math.min(width, height);
        setContainerSize(newSize);
      }
    };

    // Initial size calculation
    updateSize();

    // Recalculate on window resize
    window.addEventListener("resize", updateSize);

    return () => {
      window.removeEventListener("resize", updateSize);
    };
  }, []);

  const size = containerSize;
  const center = size / 2;
  const innerRadius = 100;
  const outerRadius = 200;
  const iconRadius = innerRadius + (outerRadius - innerRadius) * 0.4;
  const sections = Array.from({ length: totalSections }, (_, i) => i);

  // Animation timing configuration
  const totalDuration = 2;

  return (
    <div className="w-full flex flex-col items-center">
      <div
        ref={containerRef}
        className="relative w-full h-full flex items-center justify-center"
      >
        <svg
          width="100%"
          height="100%"
          viewBox={`0 0 ${size} ${size}`}
          style={{ maxWidth: size, maxHeight: size }}
        >
          {/* Define shared animation */}
          <defs>
            <style>
              {`
                @keyframes move {
                  0% { stroke-dashoffset: 0; }
                  100% { stroke-dashoffset: -40; }
                }
                
                @keyframes pulse {
                  0% { stroke-width: 2; stroke-opacity: 0.7; }
                  50% { stroke-width: 3; stroke-opacity: 0.9; }
                  100% { stroke-width: 2; stroke-opacity: 0.7; }
                }
              `}
            </style>
          </defs>

          {/* Wheel Sections with sequential highlight */}
          {sections.map(index => {
            const angleSize = (2 * Math.PI) / totalSections;
            // Add a tiny gap - just a couple of pixels
            const gapSize = 0.008; // Approximately 2-3 pixels at the circumference
            const startAngle = index * angleSize - Math.PI / 2 + gapSize;
            const endAngle = (index + 1) * angleSize - Math.PI / 2 - gapSize;

            const x1 = center + innerRadius * Math.cos(startAngle);
            const y1 = center + innerRadius * Math.sin(startAngle);
            const x2 = center + outerRadius * Math.cos(startAngle);
            const y2 = center + outerRadius * Math.sin(startAngle);
            const x3 = center + outerRadius * Math.cos(endAngle);
            const y3 = center + outerRadius * Math.sin(endAngle);
            const x4 = center + innerRadius * Math.cos(endAngle);
            const y4 = center + innerRadius * Math.sin(endAngle);

            const midAngle = (startAngle + endAngle) / 2;
            const iconX = center + iconRadius * Math.cos(midAngle);
            const iconY = center + iconRadius * Math.sin(midAngle);

            const largeArcFlag = angleSize > Math.PI ? 1 : 0;

            const sectionPath = `
              M ${x1} ${y1}
              L ${x2} ${y2}
              A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x3} ${y3}
              L ${x4} ${y4}
              A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x1} ${y1}
            `;

            const values = [];
            const keyTimes = [];
            const steps = 30;

            // For each keyframe, determine which sections should be highlighted
            for (let step = 0; step <= steps; step++) {
              // Add the keyTime first
              keyTimes.push(step / steps);

              // Calculate which section should be highlighted at this step
              const animationProgress = step / steps; // 0 to 1 for the entire animation

              // Apply a sine wave function to add slight natural acceleration/deceleration
              const easedProgress =
                animationProgress -
                0.03 * Math.sin(animationProgress * Math.PI * 2);
              const easedPosition = easedProgress * totalSections;

              // The active section is the one currently being highlighted
              const activeIndex = Math.floor(easedPosition) % totalSections;
              const prevIndex =
                activeIndex === 0 ? totalSections - 1 : activeIndex - 1;

              // Calculate progress within current section (0.0 to 1.0)
              const progressWithinSection =
                easedPosition - Math.floor(easedPosition);

              if (index === activeIndex) {
                // This is the current fully highlighted section
                // Using cubic easing for smoother transitions
                const cubicEase =
                  1 -
                  progressWithinSection *
                    progressWithinSection *
                    (0.7 - 0.2 * progressWithinSection);
                const opacity = Math.max(0.2, cubicEase);
                values.push(`rgba(187, 222, 251, ${opacity.toFixed(2)})`);
              } else if (index === prevIndex) {
                // This is the PREVIOUS section that should be half highlighted
                // Also using cubic easing for natural feel
                const cubicEase =
                  0.3 +
                  progressWithinSection *
                    progressWithinSection *
                    (0.4 + 0.1 * progressWithinSection);
                const opacity = Math.min(0.7, cubicEase);
                values.push(`rgba(187, 222, 251, ${opacity.toFixed(2)})`);
              } else {
                // All other sections - no highlight
                values.push("#E8E8E8");
              }
            }

            return (
              <g key={`section-${index}`}>
                <path
                  d={sectionPath}
                  fill="#E8E8E8"
                  stroke="#E0E0E0"
                  strokeWidth="0.5"
                >
                  <animate
                    attributeName="fill"
                    values={values.join(";")}
                    keyTimes={keyTimes.join(";")}
                    dur={`${totalDuration}s`}
                    repeatCount="indefinite"
                  />
                </path>
                <path
                  d={sectionPath}
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.5)"
                  strokeWidth="2"
                  strokeDasharray="8 12"
                  style={{ animation: "move 1.5s linear infinite" }}
                  opacity="0"
                >
                  <animate
                    attributeName="opacity"
                    values={values
                      .map(v => (v === "#E8E8E8" ? "0" : "0.25"))
                      .join(";")}
                    keyTimes={keyTimes.join(";")}
                    dur={`${totalDuration}s`}
                    repeatCount="indefinite"
                  />
                </path>

                {/* Base icon circle */}
                <circle cx={iconX} cy={iconY} r="20" fill="#E0E0E0">
                  <animate
                    attributeName="fill"
                    values={values
                      .map(v => {
                        if (v === "#E8E8E8") return "#E0E0E0";
                        const opacity = parseFloat(v.split(",")[3]);
                        if (opacity > 0.8) return "#90CAF9";
                        if (opacity > 0.4) return "rgba(144, 202, 249, 0.9)";
                        if (opacity > 0)
                          return `rgba(144, 202, 249, ${opacity.toFixed(2)})`;
                        return "#E0E0E0";
                      })
                      .join(";")}
                    keyTimes={keyTimes.join(";")}
                    dur={`${totalDuration}s`}
                    repeatCount="indefinite"
                  />
                </circle>

                {/* Pulsing effect for highlighted icons */}
                <circle
                  cx={iconX}
                  cy={iconY}
                  r="24"
                  fill="none"
                  stroke="#64B5F6"
                  strokeWidth="2"
                  opacity="0"
                  style={{ animation: "pulse 0.8s ease-in-out infinite" }}
                >
                  {/* Control visibility based on highlight state */}
                  <animate
                    attributeName="opacity"
                    values={values
                      .map(v => {
                        if (v === "#E8E8E8") return "0";
                        const opacity = parseFloat(v.split(",")[3]);
                        if (opacity > 0.7) return "1"; // Fully visible for highlighted
                        if (opacity > 0.4) return "0.5"; // Partially visible for transitioning
                        return "0"; // Hidden for non-highlighted
                      })
                      .join(";")}
                    keyTimes={keyTimes.join(";")}
                    dur={`${totalDuration}s`}
                    repeatCount="indefinite"
                  />

                  {/* Pulsing size animation */}
                  <animate
                    attributeName="r"
                    values="22;26;22"
                    dur="0.8s"
                    repeatCount="indefinite"
                  />
                </circle>
              </g>
            );
          })}

          {/* Center circle */}
          <circle
            cx={center}
            cy={center}
            r={innerRadius - 2}
            fill="#FAFAFA"
            stroke="#E8E8E8"
            strokeWidth="0.5"
          />
        </svg>
      </div>
    </div>
  );
};

export default EnergyWheelSkeleton;
