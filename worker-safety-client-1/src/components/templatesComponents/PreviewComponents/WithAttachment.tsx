import type { FieldRendererProps } from "../customisedForm.types";
import { useMutation } from "@apollo/client";
import { Icon } from "@urbint/silica";
import { isString } from "lodash-es";
import isEmpty from "lodash/isEmpty";
import React, { useContext, useState } from "react";
import * as UploadButton from "@/components/forms/Basic/UploadButton/UploadButton";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import { buildUploadFormData, upload } from "@/components/upload/utils";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import useCWFFormState from "@/hooks/useCWFFormState";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import ImageGallery from "@/components/dynamicForm/AttachmentComponents/Photos/ImageGallery";
import { UserFormModeTypes } from "../customisedForm.types";

const uploadButtonConfigs: UploadButton.UploadButtonConfigs = {
  icon: "image_alt",
  label: "Attach",
  isLoading: false,
  allowMultiple: true,
  allowedExtensions: ".apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp",
  maxFileSize: 10 * 1024 * 1024, // 10 MB
};

function withAttachmentComment(
  WrappedComponent: React.ComponentType<FieldRendererProps>
) {
  const Component = (props: FieldRendererProps) => {
    const {
      content: { properties },
      mode,
      inSummary,
    } = props;
    const disabled = mode !== UserFormModeTypes.EDIT;

    const [generateFileUploadPolicies] = useMutation(FileUploadPolicies);

    const user_comments = properties?.user_comments || "";

    const user_attachments = properties?.user_attachments || [];

    const [showComment, setShowComment] = useState<boolean>(false);

    const [showFileUpload, setShowFileUpload] = useState<boolean>(
      !!user_attachments && !!user_attachments.length && !disabled
    );

    const { setCWFFormStateDirty } = useCWFFormState();

    const { dispatch } = useContext(CustomisedFromStateContext)!;

    const toggleComment = () => {
      setShowComment(value => !value);
    };

    const toggleFileUpload = () => {
      setShowFileUpload(preValue => !preValue);
    };

    const onCommentChange = (value: string) => {
      dispatch({
        type: CF_REDUCER_CONSTANTS.ADD_FIELD_COMMENT,
        payload: {
          parentData: props.activePageDetails,
          fieldData: { comment: value, order: props.order },
          section: props.section,
        },
      });
      setCWFFormStateDirty(true);
    };

    const onFileUpload = (value: File[]) => {
      dispatch({
        type: "ADD_FIELD_ATTACHMENTS",
        payload: {
          parentData: props.activePageDetails,
          fieldData: { attachments: value, order: props.order },
          section: props.section,
        },
      });
      setCWFFormStateDirty(true);
    };
    const onFilesUpload = async (files: FileList) => {
      const uploadedUrls = [];

      for (const file of files) {
        const { data } = await generateFileUploadPolicies({
          variables: {
            filename: file.name,
            mimetype: file.type,
            count: 1,
          },
        });
        await upload(
          data.fileUploadPolicies[0].url,
          buildUploadFormData(data.fileUploadPolicies[0], file as File)
        );
        uploadedUrls.push(data.fileUploadPolicies[0].signedUrl);
      }
      onFileUpload?.(
        user_attachments
          ? [...user_attachments, ...uploadedUrls]
          : Array.from(files)
      );
    };

    const removeFile = (fileIndex: number) => {
      onFileUpload?.(
        user_attachments?.filter(
          (__: any, index: number) => index !== fileIndex
        )
      );
    };

    return (
      <div className={`flex flex-col ${inSummary ? "gap-0" : "gap-4"}`}>
        <WrappedComponent {...props} />
        {properties?.comments_allowed && !showComment && !!user_comments && (
          <span className="text-sm whitespace-pre">
            Comments: {user_comments}
          </span>
        )}
        {properties?.attachments_allowed &&
          !showFileUpload &&
          !!user_attachments.length && (
            <ImageGallery
              photos={user_attachments}
              isInputAttachment={true}
              title={"Attachments"}
              inSummary={inSummary}
            />
          )}
        <div className="flex gap-4 justify-end">
          {!inSummary && (
            <>
              {properties?.comments_allowed && !showComment && (
                <ButtonSecondary
                  className=""
                  label="Add comment"
                  iconStart="message_plus_alt"
                  onClick={toggleComment}
                  disabled={disabled}
                />
              )}
              {properties?.attachments_allowed && !showFileUpload && (
                <ButtonSecondary
                  label="Add attachment"
                  iconStart="image_alt"
                  onClick={toggleFileUpload}
                  disabled={disabled}
                />
              )}
            </>
          )}
        </div>
        {showComment && (
          <>
            <label className=" block md:text-sm text-neutral-shade-75 font-semibold leading-normal mt-4 mb-0">
              Comment
            </label>
            <textarea
              value={user_comments}
              className="w-full h-24 p-2 border-solid border-[1px] border-brand-gray-40 rounded"
              onChange={e => onCommentChange(e.target.value)}
            />
            <div className={"flex justify-end"}>
              <ButtonSecondary
                label={"Save"}
                onClick={() => setShowComment(false)}
              />
            </div>
          </>
        )}
        {showFileUpload && (
          <div className="flex flex-col">
            <div>
              <label className=" block md:text-sm text-neutral-shade-75 font-semibold leading-normal mt-4">
                Attachment
              </label>
              <div className="flex justify-between align-middle">
                <div className="md:text-sm text-neutral-shade-75 leading-normal">
                  APNG, AVIF, GIF, JPG/JPEG, PNG, SVG, or WEBP Max file size:
                  10MB
                </div>
                <UploadButton.View
                  configs={uploadButtonConfigs}
                  className="mt-2 md:mt-0"
                  onUpload={onFilesUpload}
                />
              </div>
            </div>
            <div>
              {user_attachments && !isEmpty(user_attachments) ? (
                <div className="border-2 flex flex-wrap gap-5 p-4 rounded">
                  {user_attachments.map((file: File, index: number) => (
                    <div key={file.name} className="relative w-20 h-20">
                      <img
                        src={(() => {
                          if (isString(file)) return file;
                          try {
                            return URL.createObjectURL(file);
                          } catch (e) {
                            return "";
                          }
                        })()}
                        alt="Selected"
                        height={60}
                        width={70}
                      />
                      {!disabled && (
                        <Icon
                          name="off_outline_close"
                          className="absolute right-0.5 top-0.5 text-2xl leading-6 text-white bg-black bg-opacity-60 rounded-full cursor-pointer"
                          onClick={() => removeFile(index)}
                        />
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div> No Photos uploaded</div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return Component;
}

export default withAttachmentComment;
