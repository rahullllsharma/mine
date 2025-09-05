import type { LocationSearchUsingAPIPops } from "../../customisedForm.types";
import LocationAutocomplete from "./LocationAutocomplete";

function LocationSearchUsingAPI({
  onChange,
  mode,
  value,
  properties,
  setLatitude,
  setLongitude,
  userLocationLatitude,
  userLocationLongitude,
  onClear,
}: LocationSearchUsingAPIPops) {
  return (
    <LocationAutocomplete
      value={value}
      properties={properties}
      mode={mode}
      onPlaceSelected={(_value: any) => onChange(_value)}
      setLatitude={setLatitude}
      setLongitude={setLongitude}
      userLocationLatitude={userLocationLatitude}
      userLocationLongitude={userLocationLongitude}
      onClear={onClear}
    />
  );
}

export default LocationSearchUsingAPI;
