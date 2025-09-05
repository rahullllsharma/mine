import type { IncidentId } from "@/api/codecs";
import classNames from "classnames";
import { DateTime } from "luxon";
import { Incident } from "@/api/codecs";
import { messages } from "@/locales/messages";

export function CheckedIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="28"
      height="29"
      viewBox="0 0 28 29"
      fill="none"
    >
      <rect y="0.5" width="28" height="28" rx="14" fill="#00A0CC" />
      <path
        d="M11.3484 20.9825L6.04507 15.6792L8.40341 13.3209L11.3484 16.2742L19.5966 8.01758L21.955 10.3759L11.3484 20.9825Z"
        fill="white"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="28"
      height="29"
      viewBox="0 0 28 29"
      fill="none"
    >
      <rect x="0.5" y="1" width="27" height="27" rx="13.5" fill="white" />
      <path
        d="M11.3484 20.9825L6.04507 15.6792L8.40341 13.3209L11.3484 16.2742L19.5966 8.01758L21.955 10.3759L11.3484 20.9825Z"
        fill="white"
      />
      <rect x="0.5" y="1" width="27" height="27" rx="13.5" stroke="#BDC1C3" />
    </svg>
  );
}

type IncidentProps = {
  incident: Incident;
  selected: boolean;
  onSelect: (id: IncidentId) => void;
  isReadOnly?: boolean;
};
const Incident = (props: IncidentProps): JSX.Element => {
  const { incident, onSelect, selected, isReadOnly } = props;
  const { id, description, incidentDate, incidentType } = incident;

  const handleClick = () => {
    if (!isReadOnly) {
      onSelect(id);
    }
  };

  return (
    <section
      className={classNames(
        "bg-brand-gray-10  border-2 border-brand-gray-40 px-4 py-4 rounded my-2 cursor-pointer",
        selected ? "bg-brand-urbint-20 border-brand-urbint-40" : ""
      )}
      key={id}
      onClick={isReadOnly ? undefined : handleClick} // Conditional onClick handler
    >
      <div className="align-middle flex justify-between py-2">
        <div className="flex flex-col gap-1">
          <h3 className="text-base font-semibold">{incidentType}</h3>
          <p className="text-sm text-neutral-shade-58">
            {DateTime.fromISO(incidentDate).toLocaleString({
              ...DateTime.DATE_FULL,
              weekday: "long",
            })}
          </p>
        </div>
        {selected ? <CheckedIcon /> : <CheckIcon />}
      </div>
      <div className="mt-2">
        <div className="font-semibold text-sm mb-1 text-gray-500">
          {messages.historicIncidentModalDescription}
        </div>
        <p>{description}</p>
      </div>
    </section>
  );
};

export default Incident;
