import styles from "./Loader.module.css";

type LoaderProps = {
  iconOnly?: boolean;
};

export default function Loader({ iconOnly = false }: LoaderProps): JSX.Element {
  return (
    <div className="flex items-center justify-center h-screen">
      <div>
        <div className={styles["urb-ripple"]}>
          <div></div>
          <div></div>
        </div>
      </div>
      {!iconOnly && (
        <span className={styles["urbint-brand-title"]}>Urbint</span>
      )}
    </div>
  );
}
