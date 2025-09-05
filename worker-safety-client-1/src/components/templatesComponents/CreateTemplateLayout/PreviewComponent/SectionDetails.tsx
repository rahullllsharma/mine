type SectionDetailsProps = {
  displayName: string;
  id: string;
  isActive: boolean;
};
function SectionDetails(sectionDetails: SectionDetailsProps) {
  return (
    <div>
      <h1>{sectionDetails.displayName}</h1>
      <hr />
    </div>
  );
}

export default SectionDetails;
