import type { ApiDetails } from "@/components/templatesComponents/customisedForm.types";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import { BodyText } from "@urbint/silica";
import { gql, useQuery } from "@apollo/client";

type RegionProps = {
  api_details: ApiDetails;
  user_value: string[];
};

const Region = ({ api_details, user_value }: RegionProps) => {

  const { data} = useQuery<{ regionsLibrary: LibraryRegion[] }>(
    gql(api_details.request.query as string)
  );

  const regions = data?.regionsLibrary || [];
  const selectedRegion = regions.find(region => region.id === user_value[0]);

  return (
    <BodyText>
      {selectedRegion && (selectedRegion.name)}
    </BodyText>
  );
};

export default Region;
