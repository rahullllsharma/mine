/** Forces the download of a blob or base64 on the browser */
function downloadContentAsFile(content: string | Blob, fileName: string): void {
  const url =
    typeof content === "string"
      ? `data:text/plain;base64, ${content}`
      : URL.createObjectURL(content);

  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);

  link.click();
  document.body.removeChild(link);
}

export { downloadContentAsFile };
