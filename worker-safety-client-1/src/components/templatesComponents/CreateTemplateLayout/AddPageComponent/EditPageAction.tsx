import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import style from "../createTemplateStyle.module.scss";

type EditPageActionProps = {
  onPageEditAction(action: "EDIT_PAGE_SAVE" | "EDIT_PAGE_CANCEL"): void;
  isSaveDisabled?: boolean;
};

function EditPageAction({
  onPageEditAction,
  isSaveDisabled,
}: EditPageActionProps) {
  return (
    <>
      <div className={style.addPageFormComponent}>
        <div className={style.addPageFormComponent__headerPanel}>
          <div className="pl-5">Edit Page</div>
          <div className={style.addPageFormComponent__ctaPanel}>
            <ButtonIcon
              className="text-red"
              iconName="check_big"
              onClick={() => onPageEditAction("EDIT_PAGE_SAVE")}
              disabled={isSaveDisabled}
            />

            <ButtonIcon
              iconName="close_big"
              disabled={false}
              onClick={() => {
                onPageEditAction("EDIT_PAGE_CANCEL");
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default EditPageAction;
