import type * as T from "fp-ts/lib/Task";

// This function assumes image resizing method as "contain" as this is our current desire
const drawImageToCanvas = (
  img: HTMLImageElement,
  width: number,
  height: number
): HTMLCanvasElement => {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  canvas.width = width;
  canvas.height = height;

  ctx?.save();
  ctx?.drawImage(img, 0, 0, width, height);
  ctx?.restore();

  return canvas;
};

const generateFileObjectFromBase64 =
  (base64: string) =>
  (file: File): File => {
    const encodedBase64 = base64.split(",")[1];
    const encodedByteArr = atob(encodedBase64);

    let n = encodedByteArr.length;
    const u8arr = new Uint8Array(n);

    while (n--) {
      u8arr[n] = encodedByteArr.charCodeAt(n);
    }

    return new File([u8arr], file.name, { type: file.type });
  };

const readFileAsDataUrl = async (file: File): Promise<string> => {
  const result_base64 = await new Promise<string>(resolve => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.readAsDataURL(file);
  });

  return result_base64;
};

const loadImage = async (base64: string): Promise<HTMLImageElement> => {
  const loadedImage = await new Promise<HTMLImageElement>(resolve => {
    const image = new Image();
    image.src = base64;
    image.onload = () => resolve(image);
  });

  return loadedImage;
};

const downscaleImage =
  (file: File) =>
  (maxFileSize: number): Promise<File> => {
    return new Promise<File>(async (resolve, _) => {
      if (file.size < maxFileSize) resolve(file);

      const readerResult = await readFileAsDataUrl(file);

      const image = await loadImage(readerResult);

      const { height: baseHeight, width: baseWidth } = image;

      let resizedHeight;
      let resizedWidth;

      if (baseHeight > baseWidth) {
        const targetHeight = 1080;
        resizedHeight = targetHeight;
        resizedWidth = baseWidth * (resizedHeight / baseHeight);
      } else {
        const targetWidth = 1080;
        resizedWidth = targetWidth;
        resizedHeight = baseHeight * (resizedWidth / baseWidth);
      }

      const resizedImageOnCanvas = drawImageToCanvas(
        image,
        resizedWidth,
        resizedHeight
      );

      const resizedImage = await generateFileObjectFromBase64(
        resizedImageOnCanvas.toDataURL()
      )(file);

      resolve(await resizedImage);
    });
  };

const downscaleImageAsTask =
  (file: File) =>
  (maxFileSize: number): T.Task<File> => {
    return () => downscaleImage(file)(maxFileSize);
  };

export { downscaleImage, downscaleImageAsTask };
