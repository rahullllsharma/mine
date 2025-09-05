import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import SearchSelect from "@/components/shared/inputSelect/searchSelect/SearchSelect";
import FilterWrapper from "../filterWrapper/FilterWrapper";
import { getTimeFrame } from "../utils";

type TimeFrameProps = {
  options: Readonly<TimeFrameOption[]>;
  title: string;
  onChange: (startDate: string, endDate: string) => void;
};

export type TimeFrameOption = InputSelectOption & {
  numberOfDays: number;
};

export default function TimeFrame({
  options,
  title,
  onChange,
}: TimeFrameProps): JSX.Element {
  const timeFrameSelectedHandler = (option: InputSelectOption): void => {
    const selectedOption = options.find(
      opt => option.id === opt.id
    ) as TimeFrameOption;

    const [startDate, endDate] = getTimeFrame(selectedOption.numberOfDays);
    onChange(startDate, endDate);
  };

  return (
    <FilterWrapper title={title}>
      <SearchSelect
        options={options}
        defaultOption={options[0]}
        onSelect={timeFrameSelectedHandler}
      />
    </FilterWrapper>
  );
}
