import axios from "axios";
import React, { useState, useMemo, useRef, useEffect } from "react";
import _ from "lodash";
import { InputRaw } from "@/components/forms/Basic/Input";
import { config } from "@/config";

type LocationDetails = {
  latitude: string;
  longitude: string;
};

type EboLocationAutocompleteProps = {
  onPlaceSelected: (feature: {
    place: string;
    latitude: string;
    longitude: string;
  }) => void;
  value: string;
  disabled?: boolean;
  hasError?: boolean;
  locationDetails?: LocationDetails;
  isManualCoordinates?: boolean;
};

interface Place {
  place_name: string;
  geometry: {
    coordinates: [number, number];
  };
}

const useOnClickOutside = (ref: React.RefObject<HTMLElement>, callback: () => void) => {
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [ref, callback]);
};

const EboLocationAutocomplete = ({
  onPlaceSelected,
  value,
  disabled: isReadOnly,
  hasError,
  isManualCoordinates
}: EboLocationAutocompleteProps) => {
  const [searchResults, setSearchResults] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState(value);
  const [coordinates, setCoordinates] = useState<LocationDetails>({
    latitude: "",
    longitude: "",
  });
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [manualAdd, setManualAdd] = useState(false);

  useOnClickOutside(containerRef, () => {
    if (isOpen) {
      setIsOpen(false);
      if (searchResults.length > 0 && !manualAdd) {
        setSelectedPlace("");
      }
    }
  });

  const handleCustomSearchChange = async (_value: string) => {
    setIsOpen(true);
    const response = await axios.get(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${_value}.json?access_token=${config.workerSafetyMapboxAccessToken}`
    );
    const places = response.data.features.map((feature: Place) => ({
      place_name: feature.place_name,
      geometry: feature.geometry,
    }));
    setSearchResults(places);
  };

  const handleManualAdd = () => {
    setIsOpen(false); 
    setManualAdd((prevManualAdd) => !prevManualAdd);
  };

  const applyDebounce = useMemo(
    () => _.debounce(handleCustomSearchChange, 500),
    []
  );

  const fetchLocations = (_value: string) => {

    setSelectedPlace(_value);
    if (manualAdd) {
      setIsOpen(false);
      onPlaceSelected({
        place: _value,
        latitude: coordinates.latitude,  
        longitude: coordinates.longitude,  
      });
    } else {
      applyDebounce(_value);
      setIsOpen(true);
    }
  };

  const handleClear = () => {
    setSelectedPlace("");
    if(isManualCoordinates){
      setCoordinates({latitude: coordinates.latitude, longitude: coordinates.longitude});
    }

    onPlaceSelected({
      place: "",
      latitude: coordinates.latitude,
      longitude: coordinates.longitude,
    });
  };

  const handlePlaceSelected = (place: Place) => {
    setSearchResults([]);
    setSelectedPlace(place?.place_name);
    const latitude = place?.geometry.coordinates[1].toString();
    const longitude = place?.geometry.coordinates[0].toString();

    if(isManualCoordinates){
      setCoordinates({latitude: coordinates.latitude, longitude: coordinates.longitude});
      onPlaceSelected({
        place: place?.place_name,
        latitude: coordinates.latitude,
        longitude: coordinates.longitude,
      });
    }else{
      setCoordinates({latitude: latitude, longitude: longitude});
      onPlaceSelected({
        place: place?.place_name,
        latitude: latitude,
        longitude: longitude,
      });
    }
   
    setIsOpen(false);
  };
  return (
    <div ref={containerRef}>
      <InputRaw
        label="Location"
        onChange={fetchLocations}
        value={selectedPlace || ""}
        disabled={isReadOnly}
        icon={manualAdd ? undefined : "search"}
        clearIcon={true}
        placeholder="Search Location"
        hasError={hasError}
        onClear={handleClear}
      />
       {!isReadOnly && (
      <div className="p-3 text-blue-500 cursor-pointer" onClick={handleManualAdd}>
        {manualAdd ? "Switch to lookup address" : "Switch to enter manually"}
      </div>)}
      {isOpen && (
        <div className="z-10 w-full mt-1 max-h-60 overflow-auto shadow-10 rounded outline-none css-aey3sy-Menu">
          {searchResults.length === 0 && isOpen ? (
            <div className="flex items-center p-3 text-base bg-white">
              No Location Found
            </div>
          ) : (
            searchResults.map((place: Place, index) => (
              <div
                className="flex items-center p-3 text-base cursor-pointer bg-white transition-colors duration-300 hover:bg-brand-gray-20"
                key={index}
                onClick={() => handlePlaceSelected(place)}
              >
                {place?.place_name}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default EboLocationAutocomplete;


