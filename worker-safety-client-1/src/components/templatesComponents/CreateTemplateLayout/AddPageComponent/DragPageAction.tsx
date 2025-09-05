import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import style from "../createTemplateStyle.module.scss";

type DragPageActionProps = {
  onPageDragAction(action: string): void;
};

function DragPageAction({ onPageDragAction }: DragPageActionProps) {
  return (
    <>
      <div className={style.addPageFormComponent}>
        <div className={style.addPageFormComponent__headerPanel}>
          <div className="pl-5">Arrange Page</div>
          <div className={style.addPageFormComponent__ctaPanel}>
            <ButtonIcon
              className="text-red"
              iconName="check_big"
              onClick={() => onPageDragAction("dragPageSave")}
            />

            <ButtonIcon
              iconName="close_big"
              disabled={false}
              onClick={() => {
                onPageDragAction("dragPageCancel");
              }}
            />
          </div>
        </div>
        <p className="ml-5 mt-1 text-gray-600" style={{ fontSize: "12px" }}>
          Drag and drop to re-order page
        </p>
      </div>
    </>
  );
}

export default DragPageAction;
