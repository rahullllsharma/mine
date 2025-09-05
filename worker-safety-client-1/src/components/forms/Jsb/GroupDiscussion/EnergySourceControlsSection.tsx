import type { Option } from "fp-ts/lib/Option";
import type { Either } from "fp-ts/lib/Either";
import type { Ewp, Jsb } from "@/api/codecs";
import * as A from "fp-ts/lib/Array";
import { BodyText } from "@urbint/silica";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { DateTime } from "luxon";
import { Fragment } from "react";
import { OptionalView } from "@/components/common/Optional";
import { VoltageType } from "@/api/generated/types";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type EnergySourceControlsSectionData = {
  arcFlashCategory: Option<number>;
  clearancePoints: Option<string>;
  primaryVoltage: Option<string[]>;
  secondaryVoltage: string[];
  transmissionVoltage: Option<string>;
  ewps: Ewp[];
};

export const init = (
  jsb: Jsb
): Either<string, EnergySourceControlsSectionData> => {
  const escData = pipe(
    jsb.energySourceControl,
    E.fromOption(() => "energySourceControl is missing")
  );

  return sequenceS(E.Apply)({
    arcFlashCategory: pipe(
      escData,
      E.map(({ arcFlashCategory }) => arcFlashCategory)
    ),
    clearancePoints: pipe(
      escData,
      E.map(({ clearancePoints }) =>
        pipe(
          clearancePoints,
          O.filter(val => val !== "")
        )
      )
    ),
    primaryVoltage: pipe(
      escData,
      E.map(esc =>
        pipe(
          esc.voltages,
          A.filter(voltage => voltage.type === VoltageType.Primary),
          A.map(voltage => voltage.valueStr),
          values => (values.length > 0 ? O.some(values) : O.none)
        )
      )
    ),
    secondaryVoltage: pipe(
      escData,
      E.map(esc =>
        pipe(
          esc.voltages,
          A.filter(v => v.type === VoltageType.Secondary),
          A.map(v => v.valueStr)
        )
      )
    ),
    transmissionVoltage: pipe(
      escData,
      E.map(esc =>
        pipe(
          esc.voltages,
          A.findFirst(v => v.type === VoltageType.Transmission),
          O.map(v => v.valueStr)
        )
      )
    ),
    ewps: pipe(
      escData,
      E.map(esc => esc.ewp)
    ),
  });
};
export type EnergySourceControlsSectionProps =
  EnergySourceControlsSectionData & {
    onClickEdit?: () => void;
  };

export function View({
  onClickEdit,
  arcFlashCategory,
  clearancePoints,
  primaryVoltage,
  secondaryVoltage,
  transmissionVoltage,
  ewps,
}: EnergySourceControlsSectionProps): JSX.Element {
  return (
    <GroupDiscussionSection
      title="Energy Source Controls"
      onClickEdit={onClickEdit}
    >
      <div className="flex flex-col gap-4">
        <div className="bg-white p-4">
          <OptionalView
            value={arcFlashCategory}
            render={value => (
              <div className="mb-5">
                <BodyText className="font-semibold text-sm mb-2">
                  Arc Flash Category
                </BodyText>
                <span className="text-base font-normal">{value}</span>
              </div>
            )}
          />

          <div className="flex mb-5">
            <OptionalView
              value={primaryVoltage}
              render={value => {
                const sortedVoltages = value
                  .filter(item => item !== "Other")
                  .sort((a, b) => parseFloat(a) - parseFloat(b));

                return (
                  <div className="flex-1">
                    <BodyText className="font-semibold text-sm mb-2">
                      Primary Voltage
                    </BodyText>
                    {sortedVoltages.join(", ").length > 50 ? (
                      sortedVoltages.map((item, index) => (
                        <BodyText key={index} className="font-normal text-base">
                          {item}
                        </BodyText>
                      ))
                    ) : (
                      <BodyText className="font-normal text-base">
                        {sortedVoltages.join(" kV, ")} kV
                      </BodyText>
                    )}
                  </div>
                );
              }}
            />

            {A.isNonEmpty(secondaryVoltage) && (
              <div className="flex-1">
                <BodyText className="font-semibold text-sm mb-2">
                  Secondary Voltage
                </BodyText>
                <span className="font-normal text-base">
                  {secondaryVoltage.join(" v,")} v
                </span>
              </div>
            )}

            <OptionalView
              value={transmissionVoltage}
              render={value => (
                <div className="flex-1">
                  <BodyText className="font-semibold text-sm mb-2">
                    Transmission Voltage
                  </BodyText>
                  <span className="font-normal text-base">{value} kV</span>
                </div>
              )}
            />
          </div>

          <OptionalView
            value={clearancePoints}
            render={value => (
              <div className="mb-5">
                <BodyText className="font-semibold text-sm mb-2">
                  Clearance Points
                </BodyText>
                <span className="text-base font-normal">{value}</span>
              </div>
            )}
          />
        </div>

        {ewps.map(ewp => (
          <div key={ewp.id} className="bg-white p-4">
            <div className="mb-5">
              <BodyText className="font-semibold text-sm mb-2">EWP</BodyText>
              <span className="font-normal text-base">{ewp.id}</span>
            </div>

            <div className="flex mb-5">
              <div className="flex-1">
                <BodyText className="font-semibold text-sm mb-2">
                  Time Issued
                </BodyText>
                <span className="font-normal text-base">
                  {ewp.metadata.issued.toLocaleString(DateTime.TIME_SIMPLE)}
                </span>
              </div>

              <OptionalView
                value={ewp.metadata.completed}
                render={value => (
                  <div className="flex-1">
                    <BodyText className="font-semibold text-sm mb-2">
                      Time Completed
                    </BodyText>
                    <span className="font-normal text-base">
                      {value.toLocaleString(DateTime.TIME_SIMPLE)}
                    </span>
                  </div>
                )}
              />
            </div>

            <div className="mb-5">
              <BodyText className="font-semibold text-sm mb-2">
                Procedure
              </BodyText>
              <span className="font-normal text-base">
                {ewp.metadata.procedure}
              </span>
            </div>

            <div className="flex mb-5">
              <div className="flex-1">
                <BodyText className="font-semibold text-sm mb-2">
                  Issued By
                </BodyText>
                <span className="font-normal text-base">
                  {ewp.metadata.issuedBy}
                </span>
              </div>

              <div className="flex-1">
                <BodyText className="font-semibold text-sm mb-2">
                  Received By
                </BodyText>
                <span className="font-normal text-base">
                  {ewp.metadata.receivedBy}
                </span>
              </div>
            </div>

            <div className="flex mb-5">
              {ewp.referencePoints.map((referencePoint, i) => (
                <div key={i} className="flex-1">
                  <BodyText className="font-semibold text-sm mb-2">
                    Reference Point {i + 1}
                  </BodyText>
                  <span className="font-normal text-base">
                    {referencePoint}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex mb-5">
              {ewp.equipmentInformation.map((equipment, i) => (
                <Fragment key={i}>
                  <div className="flex-1">
                    <BodyText className="font-semibold text-sm mb-2">
                      Circuit Breaker #
                    </BodyText>
                    <span className="font-normal text-base">
                      {equipment.circuitBreaker}
                    </span>
                  </div>
                  <div className="flex-1">
                    <BodyText className="font-semibold text-sm mb-2">
                      Transformer #
                    </BodyText>
                    <span className="font-normal text-base">
                      {equipment.transformer}
                    </span>
                  </div>
                </Fragment>
              ))}
            </div>
          </div>
        ))}
      </div>
    </GroupDiscussionSection>
  );
}
