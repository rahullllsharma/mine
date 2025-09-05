import SectionDetails from "./SectionDetails";

type SectionDetailsModel = {
  displayName: string;
  id: string;
  isActive: boolean;
};
type SectionListProps = {
  data: SectionDetailsModel[];
  selectedSectionId: string;
};
function SectionList(sectionListProps: SectionListProps) {
  return (
    <>
      {sectionListProps.data.map(details => (
        <SectionDetails
          displayName={details.displayName}
          key={details.id}
          id={details.id}
          isActive={true}
        ></SectionDetails>
      ))}
    </>
  );
}

export default SectionList;
