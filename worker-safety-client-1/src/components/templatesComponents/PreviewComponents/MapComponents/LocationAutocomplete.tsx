import type { LocationAutocompleteProps } from "../../customisedForm.types";
import axios from "axios";
import React, {
  useContext,
  useEffect,
  useState,
  useCallback,
  useRef,
} from "react";
import { debounce } from "lodash-es";
import { InputRaw } from "@/components/forms/Basic/Input";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { config } from "@/config";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { UserFormModeTypes } from "../../customisedForm.types";

const LocationAutocomplete = ({
  mode,
  onPlaceSelected,
  value,
  properties,
  setLatitude,
  setLongitude,
  userLocationLatitude,
  userLocationLongitude,
  onClear,
}: LocationAutocompleteProps) => {
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlace, setSelectedPlace] = useState(value);
  const currentSearchQueryRef = useRef<string>("");

  const [error, setError] = useState(false);
  const { state } = useContext(CustomisedFromStateContext)!;

  const toastCtx = useContext(ToastContext);

  useEffect(() => {
    onPlaceSelected(selectedPlace);
  }, [selectedPlace]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (properties?.is_mandatory && !selectedPlace?.trim()) {
          setError(true);
        } else {
          setError(false);
          onPlaceSelected(selectedPlace);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [
    selectedPlace,
    onPlaceSelected,
    properties?.is_mandatory,
    state.form.component_data?.location_data?.name,
  ]);

  useEffect(() => {
    if (error) {
      if (properties?.is_mandatory && !selectedPlace?.trim()) {
        setError(true);
      } else {
        setError(false);
      }
    }
  }, [error, selectedPlace]);

  const handleGeolocationError = (message: string) => {
    toastCtx?.pushToast("error", message);
  };

  const getCustomSearchUrl = (searchQuery: string) => {
    if (userLocationLatitude && userLocationLongitude) {
      return `https://api.mapbox.com/search/geocode/v6/forward?q=${searchQuery}&proximity=${userLocationLongitude},${userLocationLatitude}&access_token=${config.workerSafetyMapboxAccessToken}`;
    }
    return `https://api.mapbox.com/search/geocode/v6/forward?q=${searchQuery}&access_token=${config.workerSafetyMapboxAccessToken}`;
  };

  const handleSearchInputChange = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await axios.get(getCustomSearchUrl(searchQuery));

      if (currentSearchQueryRef.current === searchQuery) {
        const places = response.data.features.map((feature: any) => ({
          place_name: feature.properties.full_address ?? "",
          geometry: feature.geometry,
        }));

        setSearchResults(places);
      }
    } catch (_error: any) {
      if (currentSearchQueryRef.current === searchQuery) {
        handleGeolocationError("Error fetching search results");
        console.error("Error fetching search results:", _error.message);
      }
    }
  };

  const debouncedSearch = useCallback(
    debounce((searchQuery: string) => {
      currentSearchQueryRef.current = searchQuery;
      handleSearchInputChange(searchQuery);
    }, 500),
    [userLocationLatitude, userLocationLongitude]
  );

  const handleCustomSearchChange = (inputValue: string) => {
    setSelectedPlace(inputValue);

    debouncedSearch.cancel();

    if (inputValue.trim()) {
      debouncedSearch(inputValue);
    } else {
      setSearchResults([]);
      currentSearchQueryRef.current = "";
    }
  };

  useEffect(() => {
    setSelectedPlace(value);
    if (!value || value === "") {
      setSearchResults([]);
      debouncedSearch.cancel();
      currentSearchQueryRef.current = "";
    }
  }, [value, debouncedSearch]);

  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  const handlePlaceSelected = (place: any) => {
    setSearchResults([]);
    setSelectedPlace(place?.place_name);
    const coordinates = place.geometry?.coordinates;
    if (Array.isArray(coordinates) && coordinates.length === 2) {
      const [longitude, latitude] = coordinates;
      setLatitude && setLatitude(latitude.toString());
      setLongitude && setLongitude(longitude.toString());
    }
    // onPlaceSelected(place?.place_name);
  };

  const handleOnClearClick = () => {
    setSelectedPlace("");
    setSearchResults([]);
    setLatitude && setLatitude("");
    setLongitude && setLongitude("");
    currentSearchQueryRef.current = "";
    debouncedSearch.cancel();
  };

  return (
    <>
      <div>
        <InputRaw
          onChange={handleCustomSearchChange}
          value={selectedPlace || ""}
          disabled={
            mode === UserFormModeTypes.BUILD ||
            mode === UserFormModeTypes.PREVIEW ||
            mode === UserFormModeTypes.PREVIEW_PROPS
          }
          icon={"search"}
          dataTestId="input-location-autocomplete"
          clearIcon={true}
          placeholder="Search Location"
          hasError={error}
          onClear={onClear ? onClear : handleOnClearClick}
        />
        <div className="z-10 w-full mt-2 max-h-60 overflow-auto shadow-10 rounded   outline-none css-aey3sy-Menu">
          {searchResults.map((place: any, index) => (
            <div
              className={`flex items-center p-3 text-base cursor-pointer bg-white transition-colors duration-300 hover:bg-brand-gray-20`}
              key={index}
              onClick={() => handlePlaceSelected(place)}
            >
              {place?.place_name}
            </div>
          ))}
        </div>
      </div>
      {error && properties.is_mandatory && (
        <p className="text-red-500">This is required</p>
      )}
    </>
  );
};

export default LocationAutocomplete;
