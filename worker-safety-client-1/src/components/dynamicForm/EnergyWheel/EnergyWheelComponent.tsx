import type {
  EnergyType,
  EnergyWheelProps,
} from "../../templatesComponents/customisedForm.types";
import React, { useState } from "react";
import {
  ENERGY_TYPE_COLOR,
  ENERGY_TYPES,
} from "../../templatesComponents/customisedForm.types";

export default function EnergyWheelComponent({
  callback,
  status,
  readOnly,
}: EnergyWheelProps) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  // Fixed size for the SVG viewBox
  const size = 600;
  const center = size / 2;
  const innerRadius = size * 0.21;
  const outerRadius = size * 0.42;
  const labelRadius = innerRadius + (outerRadius - innerRadius) * 0.85;
  const iconRadius = innerRadius + (outerRadius - innerRadius) * 0.4;

  // Dynamic icon sizing - larger proportion of the wheel
  const iconSize = size * 0.1; // 10% of the wheel size

  const buttons = Object.keys(ENERGY_TYPES).map(key => ({
    icon: `/assets/CWF/EnergyWheel/${key.toLowerCase()}.svg`,
    label: ENERGY_TYPES[key as EnergyType],
    color: ENERGY_TYPE_COLOR[ENERGY_TYPES[key as EnergyType]],
    selected: status[key as EnergyType] ?? false,
  }));

  return (
    <div className="relative w-full aspect-square flex items-center justify-center">
      <svg
        className="w-full h-full max-w-full max-h-full"
        viewBox={`0 0 ${size} ${size}`}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          {buttons.map((_button, index) => {
            const angleSize = (2 * Math.PI) / buttons.length;
            const startAngle = index * angleSize - Math.PI / 2;
            const endAngle = (index + 1) * angleSize - Math.PI / 2;
            const x1 = center + labelRadius * Math.cos(startAngle);
            const y1 = center + labelRadius * Math.sin(startAngle);
            const x2 = center + labelRadius * Math.cos(endAngle);
            const y2 = center + labelRadius * Math.sin(endAngle);
            const largeArcFlag = angleSize > Math.PI ? 1 : 0;
            const textPathD = `M ${x1} ${y1} A ${labelRadius} ${labelRadius} 0 ${largeArcFlag} 1 ${x2} ${y2}`;
            const flippedTextPathD = `M ${x2} ${y2} A ${labelRadius} ${labelRadius} 0 ${largeArcFlag} 0 ${x1} ${y1}`;
            return (
              <React.Fragment key={`paths-${index}`}>
                <path id={`text-path-${index}`} d={textPathD} fill="none" />
                <path
                  id={`flipped-text-path-${index}`}
                  d={flippedTextPathD}
                  fill="none"
                />
              </React.Fragment>
            );
          })}
        </defs>
        {/* Wheel Sections */}
        {buttons.map((button, index) => {
          const angleSize = (2 * Math.PI) / buttons.length;
          const startAngle = index * angleSize - Math.PI / 2 + 0.003; // Smaller offset for minimal gap
          const endAngle = (index + 1) * angleSize - Math.PI / 2 - 0.003; // Smaller offset for minimal gap

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
          // Determine if text needs to be flipped (bottom half of wheel)
          const needsFlippedText = midAngle > 0 && midAngle < Math.PI;
          const sectionPath = `
            M ${x1} ${y1}
            L ${x2} ${y2}
            A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x3} ${y3}
            L ${x4} ${y4}
            A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x1} ${y1}
          `;

          const isHovered = hoverIndex === index;
          const scale = isHovered ? 1.05 : 1;
          const transformOrigin = `${center}px ${center}px`;

          return (
            <g
              key={`section-${index}`}
              className="cursor-pointer transition-all duration-200"
              onClick={() =>
                !readOnly &&
                callback(Object.keys(ENERGY_TYPES)[index] as EnergyType)
              }
              onMouseEnter={() => !readOnly && setHoverIndex(index)}
              onMouseLeave={() => setHoverIndex(null)}
              style={{ transform: `scale(${scale})`, transformOrigin }}
            >
              <path
                d={sectionPath}
                fill={
                  button.selected
                    ? button.color
                    : isHovered
                    ? `${button.color}4D`
                    : "#C0C7C9"
                }
              />

              <image
                href={button.icon}
                x={iconX - iconSize / 2}
                y={iconY - iconSize / 2}
                width={iconSize}
                height={iconSize}
                className={`pointer-events-none ${
                  status[Object.keys(ENERGY_TYPES)[index] as EnergyType]
                    ? "opacity-100"
                    : "opacity-30"
                }`}
              />

              <text
                className="pointer-events-none select-none font-sans"
                fill="black"
                fontSize={`${size < 400 ? 12 : 14}`}
                textAnchor="middle"
                fontWeight="bold"
              >
                <textPath
                  href={`#${
                    needsFlippedText ? "flipped-text-path" : "text-path"
                  }-${index}`}
                  startOffset="50%"
                  dominantBaseline="middle"
                >
                  {button.label}
                </textPath>
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
