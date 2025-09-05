import type { Hazard } from "@/api/codecs";
import type { Option } from "fp-ts/lib/Option";
import type {
  Action,
  HazardFieldValues,
} from "../HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import * as O from "fp-ts/lib/Option";
import { Ord } from "fp-ts/number";
import * as A from "fp-ts/lib/Array";
import * as M from "fp-ts/lib/Map";
import * as Tup from "fp-ts/lib/Tuple";
import { pipe } from "fp-ts/lib/function";
import { HazardComponent } from "./Hazard";

export type HazardWrapperProps = {
  hazard: Hazard;
  observationsForHazard: Option<Map<number, HazardFieldValues>>;
  dispatch: (action: Action) => void;
  closeDropDownOnOutsideClick?: boolean;
  isReadOnly: boolean;
};

const generateAdditionalTitle = (length: number) => (id: number) =>
  pipe(
    length,
    O.fromPredicate(l => l > 1),
    O.map(l => ` - ${id + 1}/${l}`),
    O.getOrElse(() => "")
  );

const HazardWrapper = ({
  hazard,
  observationsForHazard,
  dispatch,
  closeDropDownOnOutsideClick,
  isReadOnly,
}: HazardWrapperProps) => {
  if (O.isNone(observationsForHazard)) {
    return (
      <HazardComponent
        isBaseHazard={true}
        hazard={hazard}
        formValues={O.none}
        dispatch={dispatch}
        additionalTitle={generateAdditionalTitle(0)(0)}
        allowCopy={false}
        allowDelete={false}
        closeDropDownOnOutsideClick={closeDropDownOnOutsideClick}
        isReadOnly={isReadOnly}
      />
    );
  } else {
    const hazardsWithSameHazard = M.toArray(Ord)(observationsForHazard.value);

    return (
      <div className="flex flex-col gap-4">
        {pipe(
          hazardsWithSameHazard,
          A.mapWithIndex((id, haz) => (
            <HazardComponent
              key={Tup.fst(haz)}
              isBaseHazard={id === 0}
              copyId={O.some(Tup.fst(haz))}
              hazard={hazard}
              formValues={O.some(Tup.snd(haz))}
              dispatch={dispatch}
              additionalTitle={pipe(
                id,
                generateAdditionalTitle(hazardsWithSameHazard.length)
              )}
              allowCopy={true}
              allowDelete={id !== 0}
              closeDropDownOnOutsideClick={closeDropDownOnOutsideClick}
              isReadOnly={isReadOnly}
            />
          ))
        )}
      </div>
    );
  }
};

export default HazardWrapper;
