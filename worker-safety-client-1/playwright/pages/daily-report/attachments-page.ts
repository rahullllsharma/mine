import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportAttachmentsPage extends BasePage {
  // Selectors
  readonly headerPhotos: Locator = this.getHeaderByText("h6", "Photos");
  readonly photoFormatsText: Locator = this.getByText(
    "APNG, AVIF, GIF, JPG, JPEG, PNG, SVG, WEBP"
  );
  readonly photoSizeText: Locator = this.getByText("Max file size: 10MB");
  readonly noPhotoUploadedText: Locator = this.getByText("No Photos uploaded");
  readonly headerDocs: Locator = this.getHeaderByText("h6", "Documents");
  readonly headerDocsFormatsText: Locator = this.getByText(
    "PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX"
  );
  readonly noDocsUploaded: Locator = this.getByText("No documents uploaded");
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Attachments DIR section
   */
  async updateAttachments() {
    console.log("Update Attachments DIR section");
    // TODO: Review when WSAPP-799 is fixed
    await expect(this.headerPhotos).toBeVisible();
    await expect(this.photoFormatsText).toBeVisible();
    await expect(this.photoSizeText.first()).toBeVisible();
    await expect(this.noPhotoUploadedText).toBeVisible();

    // TODO: Review when WSAPP-799 is fixed
    await expect(this.headerDocs).toBeVisible();
    await expect(this.headerDocsFormatsText).toBeVisible();
    await expect(this.photoSizeText.nth(1)).toBeVisible();

    await expect(this.noDocsUploaded).toBeVisible();
    await this.saveContinueBtn.click();
  }
}
