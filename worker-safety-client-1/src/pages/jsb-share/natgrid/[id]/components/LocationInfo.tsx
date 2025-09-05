import type { WorkLocationWithVoltageInfo } from "@/types/natgrid/jobsafetyBriefing";
import { useState, useEffect } from "react";
import { BodyText, Icon, Subheading } from "@urbint/silica";

type LocationInfoProps = {
  locationInfo: WorkLocationWithVoltageInfo[];
  printPdf: boolean;
};

const LocationInfo = ({ locationInfo, printPdf }: LocationInfoProps) => {
  const [openCards, setOpenCards] = useState<number[]>([]);

  useEffect(() => {
    if (locationInfo?.length) {
      if (printPdf) {
        setOpenCards(
          Array.from({ length: locationInfo.length }, (_, index) => index)
        );
      } else setOpenCards([0]);
    }
  }, [locationInfo, printPdf]);

  const toggleCard = (idx: number) =>
    setOpenCards(prev =>
      prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]
    );

  if (!locationInfo?.length) return null;

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Location Information
      </Subheading>

      <div className="bg-brand-gray-10 p-2 mt-4 mb-4 gap-3 flex flex-col">
        {locationInfo.map((loc, idx) => (
          <div
            key={idx}
            className="bg-white rounded p-2 border border-brand-gray-20 shadow-10"
          >
            <button
              onClick={() => toggleCard(idx)}
              className="w-full flex items-center justify-between p-4 pt-1 pb-1 text-left"
            >
              <p className="font-subheading text-neutrals-primary text-[16px]">
                {loc.address ?? `Location ${idx + 1}`}
              </p>
              <Icon
                name={
                  openCards.includes(idx) ? "chevron_down" : "chevron_right"
                }
                style={{ fontSize: "28px" }}
              />
            </button>
            <div
              className={`rounded bg-brand-gray-10 ${
                printPdf
                  ? "flex flex-col max-h-[2000px] opacity-100 p-4 mt-4 gap-3"
                  : openCards.includes(idx)
                  ? "flex flex-col max-h-[2000px] opacity-100 p-4 mt-4 gap-3"
                  : "max-h-0 opacity-0 overflow-hidden"
              }`}
            >
              <div className="flex flex-grow flex-wrap">
                <div className="flex flex-col flex-grow">
                  <BodyText className="text-brand-gray-70 font-medium">
                    Latitude
                  </BodyText>
                  <BodyText>{loc.gpsCoordinates?.latitude}</BodyText>
                </div>
                <div className="flex flex-col flex-grow">
                  <BodyText className="text-brand-gray-70 font-medium">
                    Longitude
                  </BodyText>
                  <BodyText>{loc.gpsCoordinates?.longitude}</BodyText>
                </div>
              </div>
              <div className="flex flex-col flex-grow">
                <BodyText className="text-brand-gray-70 font-medium">
                  Nearest intersection / Landmark (or other location details)
                </BodyText>
                <BodyText>{loc.landmark}</BodyText>
              </div>
              <div className="flex flex-col flex-grow">
                <BodyText className="text-brand-gray-70 font-medium">
                  Circuits
                </BodyText>
                <BodyText>{loc.circuit}</BodyText>
              </div>
              <div className="flex flex-col flex-grow">
                <BodyText className="text-brand-gray-70 font-medium">
                  Voltages
                </BodyText>
                <BodyText>{loc.voltageInformation?.voltage?.value}</BodyText>
              </div>
              <div className="flex flex-col flex-grow">
                <BodyText className="text-brand-gray-70 font-medium">
                  Minimum Approach Distance
                </BodyText>
                <div className="flex flex-grow flex-wrap">
                  <div className="flex flex-col flex-grow">
                    <BodyText className="text-brand-gray-70 font-medium">
                      Phase to Phase
                    </BodyText>
                    <BodyText>
                      {
                        loc.voltageInformation?.minimumApproachDistance
                          ?.phaseToPhase
                      }
                    </BodyText>
                  </div>
                  <div className="flex flex-col flex-grow">
                    <BodyText className="text-brand-gray-70 font-medium">
                      Phase to Ground
                    </BodyText>
                    <BodyText>
                      {
                        loc.voltageInformation?.minimumApproachDistance
                          ?.phaseToGround
                      }
                    </BodyText>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

export default LocationInfo;
