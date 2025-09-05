import Loader from "@/components/shared/loader/Loader";
import style from "./CSFLoader.module.scss";

const CSFLoader = () => {
  return (
    <div className={style.loaderParent}>
      <span className="w-60">
        <Loader />
      </span>
    </div>
  );
};

export default CSFLoader;

//w-screen h-screen fixed flex items-center justify-center bg-white
