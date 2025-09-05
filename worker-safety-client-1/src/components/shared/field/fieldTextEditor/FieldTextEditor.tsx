import type { FieldProps } from "../Field";
import type { Editor as TinyMCEEditor } from "tinymce";
import React, { useState } from "react";
import { Editor } from "@tinymce/tinymce-react";
import { useMutation } from "@apollo/client";
import { config } from "@/config";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import { buildUploadFormData, upload } from "@/components/upload/utils";
import Field from "../Field";
import Loader from "../../loader/Loader";

type plugin =
  | "anchor"
  | "autolink"
  | "autoresize"
  | "charmap"
  | "codesample"
  | "emoticons"
  | "image"
  | "link"
  | "lists"
  | "media"
  | "searchreplace"
  | "table"
  | "visualblocks"
  | "wordcount";

export type FieldTextEditorProps = FieldProps & {
  id?: string;
  name?: string;
  value: string;
  placeholder?: string;
  isDisabled?: boolean;
  readOnly?: boolean;
  hasError?: boolean;
  onChange: (value: string) => void;
  minHeight?: number;
  maxHeight?: number;
  menubar?: boolean;
  plugins?: plugin[];
  toolbar?: string;
  resize?: boolean;
  className?: string;
};

// Custom Table Grid Picker Component
const TableGridPicker = ({
  onSelect,
  onClose,
}: {
  onSelect: (rows: number, cols: number) => void;
  onClose: () => void;
}) => {
  const [hoveredCell, setHoveredCell] = useState({ row: 0, col: 0 });
  const [dimensions, setDimensions] = useState({ rows: 0, cols: 0 });
  const maxRows = 10;
  const maxCols = 10;

  const handleMouseEnter = (row: number, col: number) => {
    setHoveredCell({ row, col });
    setDimensions({ rows: row + 1, cols: col + 1 });
  };

  const handleMouseLeave = () => {
    setHoveredCell({ row: -1, col: -1 });
    setDimensions({ rows: 0, cols: 0 });
  };

  const handleClick = () => {
    if (dimensions.rows > 0 && dimensions.cols > 0) {
      onSelect(dimensions.rows, dimensions.cols);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div
        className="bg-white p-4 rounded-lg shadow-xl"
        onMouseLeave={handleMouseLeave}
      >
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-gray-600">
            {dimensions.rows > 0
              ? `${dimensions.rows}x${dimensions.cols} Table`
              : "Select table size"}
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        <div
          className="grid gap-0.5 bg-gray-100 p-2 rounded"
          style={{
            gridTemplateColumns: `repeat(${maxCols}, 1.5rem)`,
            gridTemplateRows: `repeat(${maxRows}, 1.5rem)`,
          }}
        >
          {Array.from({ length: maxRows }, (_1, row) =>
            Array.from({ length: maxCols }, (_2, col) => (
              <div
                key={`${row}-${col}`}
                className={`
                  w-6 h-6 border transition-all duration-75
                  ${
                    row <= hoveredCell.row && col <= hoveredCell.col
                      ? "bg-blue-200 border-blue-400"
                      : "bg-white border-gray-200 hover:border-gray-300"
                  }
                  cursor-pointer
                `}
                onMouseEnter={() => handleMouseEnter(row, col)}
                onClick={handleClick}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Main Editor Component
const FieldTextEditor = function ({
  id = "",
  name = "",
  value = "",
  minHeight = 400,
  maxHeight = 800,
  isDisabled = false,
  onChange,
  resize = false,
  plugins = [
    "anchor",
    "autoresize",
    "charmap",
    "codesample",
    "emoticons",
    "autolink",
    "image",
    "link",
    "lists",
    "media",
    "searchreplace",
    "table",
    "visualblocks",
    "wordcount",
  ],
  toolbar = "undo redo | blocks fontfamily fontsize forecolor | bold italic underline strikethrough | checklist numlist bullist indent outdent align lineheight | link image media table",
  ...fieldProps
}: FieldTextEditorProps) {
  const [isLoading, setIsLoading] = React.useState(true);
  const [showGridPicker, setShowGridPicker] = useState(false);
  const editorRef = React.useRef<TinyMCEEditor | null>(null);

  const [generateFileUploadPolicies] = useMutation(FileUploadPolicies);

  const handleTableInsert = (rows: number, cols: number) => {
    if (editorRef.current) {
      editorRef.current.execCommand("mceInsertTable", false, {
        rows,
        columns: cols,
        options: { headerRows: 0, headerColumns: 0 },
      });
    }
  };

  const handleImageUpload = async (
    blobInfo: { blob: () => Blob; filename: () => string },
    progress: (percent: number) => void
  ): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        progress(0);
        const { data } = await generateFileUploadPolicies({
          variables: { count: 1 },
        });

        if (!data?.fileUploadPolicies?.[0]) {
          reject("Failed to get upload policy");
          return;
        }

        const fileUploadPolicy = data.fileUploadPolicies[0];
        progress(30);

        const file = new File([blobInfo.blob()], blobInfo.filename(), {
          type: blobInfo.blob().type,
        });

        const uploadResult = await upload(
          fileUploadPolicy.url,
          buildUploadFormData(fileUploadPolicy, file)
        );

        if (uploadResult === "success") {
          progress(100);
          resolve(fileUploadPolicy.signedUrl);
        } else {
          reject("Upload failed");
        }
      } catch (error) {
        console.error("Image upload error:", error);
        reject("Upload failed: " + error);
      }
    });
  };

  const setupEditor = (editor: TinyMCEEditor) => {
    editorRef.current = editor;

    editor.on("init", () => {
      // Override default table button and menu item
      editor.ui.registry.addMenuItem("table", {
        text: "Table",
        icon: "table",
        onAction: () => {
          setShowGridPicker(true);
        },
      });

      editor.ui.registry.addButton("table", {
        icon: "table",
        tooltip: "Table",
        onAction: () => {
          setShowGridPicker(true);
        },
      });
    });
  };

  return (
    <Field {...fieldProps} htmlFor={id}>
      {isLoading && <Loader />}
      <div style={{ display: isLoading ? "none" : "block" }}>
        <Editor
          id={id}
          apiKey={config?.tinyMceApiKey}
          value={value}
          disabled={isDisabled}
          textareaName={name}
          onEditorChange={onChange}
          onLoadContent={() => setIsLoading(false)}
          init={{
            content_security_policy:
              "script-src 'self' *.tinymce.com *.tiny.cloud 'unsafe-inline' 'unsafe-eval'; script-src-elem *.urbinternal.com *.tinymce.com *.tiny.cloud 'unsafe-inline' 'unsafe-eval'",
            branding: false,
            min_height: minHeight,
            max_height: maxHeight,
            menubar: false,
            plugins,
            toolbar,
            resize,
            content_style:
              "body { font-family:Helvetica,Arial,sans-serif; font-size:14px }",
            automatic_uploads: true,
            file_picker_types: "image",
            images_upload_handler: handleImageUpload,
            images_upload_url: "",
            images_upload_base_path: "",
            images_reuse_filename: false,
            paste_data_images: false,
            paste_block_drop: false,
            paste_webkit_styles: "none",
            paste_remove_styles_if_webkit: true,
            image_advtab: false,
            image_caption: true,
            image_list: false,
            image_title: false,
            image_description: false,
            image_dimensions: true,
            image_alt_text: true,
            // Table configurations
            table_grid: false, // Disable default grid picker
            table_tab_navigation: true,
            table_advtab: true,
            table_cell_advtab: true,
            table_row_advtab: true,
            table_resize_bars: true,
            table_toolbar:
              "tableprops tabledelete | tableinsertrowbefore tableinsertrowafter tabledeleterow | tableinsertcolbefore tableinsertcolafter tabledeletecol",
            table_default_styles: {
              width: "100%",
              borderCollapse: "collapse",
            },
            table_appearance_options: true,
            table_clone_elements: "strong em a",
            setup: setupEditor,
          }}
        />
      </div>
      {showGridPicker && (
        <TableGridPicker
          onSelect={handleTableInsert}
          onClose={() => setShowGridPicker(false)}
        />
      )}
    </Field>
  );
};

export default FieldTextEditor;
