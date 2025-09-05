import type { RefObject } from "react";
import { useCallback, useState } from "react";

interface FsDocument extends Omit<Document, "webkitExitFullscreen"> {
  mozFullScreenElement?: Element;
  msFullscreenElement?: Element;
  webkitFullscreenElement?: Element;
  webkitExitFullscreen?: () => void;
}

interface FsDocumentElement extends HTMLElement {
  msRequestFullscreen?: () => void;
  mozRequestFullScreen?: () => void;
  webkitRequestFullscreen?: () => void;
}

export function isFullScreen(): boolean {
  const fsDoc = document as FsDocument;

  return !!(
    fsDoc.fullscreenElement ||
    fsDoc.mozFullScreenElement ||
    fsDoc.webkitFullscreenElement ||
    fsDoc.msFullscreenElement
  );
}

export default function useFullscreen(
  elementRef: RefObject<FsDocumentElement>
) {
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const toggle = useCallback(() => {
    if (isFullScreen()) {
      const fsDoc = document as FsDocument;
      if (fsDoc.exitFullscreen) {
        fsDoc.exitFullscreen();
        setIsFullscreen(false);
      } else if (fsDoc.mozCancelFullScreen) {
        fsDoc.mozCancelFullScreen();
        setIsFullscreen(false);
      } else if (fsDoc.webkitExitFullscreen) {
        fsDoc.webkitExitFullscreen();
        setIsFullscreen(false);
      } else if (fsDoc.msExitFullscreen) {
        fsDoc.msExitFullscreen();
        setIsFullscreen(false);
      }
    } else if (elementRef.current) {
      if (elementRef.current.requestFullscreen) {
        elementRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else if (elementRef.current.mozRequestFullScreen) {
        elementRef.current.mozRequestFullScreen();
        setIsFullscreen(true);
      } else if (elementRef.current.webkitRequestFullscreen) {
        elementRef.current.webkitRequestFullscreen();
        setIsFullscreen(true);
      } else if (elementRef.current.msRequestFullscreen) {
        elementRef.current.msRequestFullscreen();
        setIsFullscreen(true);
      }
    }
  }, [elementRef]);

  return { isFullscreen, toggle };
}
