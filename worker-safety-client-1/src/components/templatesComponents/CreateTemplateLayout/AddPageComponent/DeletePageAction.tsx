import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import style from "../createTemplateStyle.module.scss";

type PageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};
type DeletePageActionProps = {
  deletePageDetails: PageDetails[];
  onPageDeleteAction: (action: string) => void;
};
function DeletePageAction({
  deletePageDetails,
  onPageDeleteAction,
}: DeletePageActionProps) {
  const anyPageCheckedToDelete = () => {
    const hasDeleteParentPageTrue = deletePageDetails.some(
      obj => obj.deleteParentPage === true
    );

    // Check if any object has subPages array with length greater than 0
    const hasSubPages = deletePageDetails.some(obj => obj.subPages.length > 0);

    return hasDeleteParentPageTrue || hasSubPages;
  };

  return (
    <>
      <div className={style.addPageFormComponent}>
        <div className={style.addPageFormComponent__headerPanel}>
          <div className="pl-5">Delete Page</div>
          <div className={style.addPageFormComponent__ctaPanel}>
            {anyPageCheckedToDelete() && (
              <ButtonIcon
                className="text-red"
                iconName="check_big"
                onClick={() => onPageDeleteAction("delete")}
              />
            )}

            <ButtonIcon
              iconName="close_big"
              disabled={false}
              onClick={() => {
                onPageDeleteAction("deleteCancel");
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default DeletePageAction;
