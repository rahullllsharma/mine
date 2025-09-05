import type { FileProperties, Jsb } from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import * as E from "fp-ts/lib/Either";
import * as A from "fp-ts/lib/Array";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { sequenceS } from "fp-ts/lib/Apply";
import { Icon, SectionHeading } from "@urbint/silica";
import Image from "next/image";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type AttachmentsSectionData = {
  photos: FileProperties[];
  documents: FileProperties[];
};

export const init = (jsb: Jsb): Either<string, AttachmentsSectionData> => {
  const result = sequenceS(E.Apply)({
    photos: pipe(
      jsb.photos,
      E.fromOption(() => "Photos are missing"),
      E.map(A.map(item => item))
    ),
    documents: pipe(
      jsb.documents,
      E.fromOption(() => "Documents are missing"),
      E.map(A.map(item => item))
    ),
  });

  return result;
};

export type AttachmentsSectionProps = AttachmentsSectionData & {
  onClickEdit?: () => void;
};

export function View({
  photos,
  documents,
  onClickEdit,
}: AttachmentsSectionProps): JSX.Element {
  return (
    <GroupDiscussionSection title="Attachments" onClickEdit={onClickEdit}>
      <SectionHeading className="w-full text-xl font-semibold">
        Photos ({photos.length})
      </SectionHeading>
      {photos.length > 0 ? (
        onClickEdit ? (
          <div className="w-full flex flex-row flex-wrap min-h-[80px] justify-start items-start gap-4 p-2 border-neutral-shade-18 border rounded">
            {pipe(
              photos,
              A.map(f => (
                <div key={f.name} className="relative w-20 h-20">
                  <Image
                    src={f.signedUrl}
                    height={80}
                    width={80}
                    alt={f.name}
                    className="absolute inset-0 z-0 object-cover object-left-top"
                  />
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-4 p-2 border-neutral-shade-18 border rounded">
            {pipe(
              photos,
              A.map(f => (
                <div key={f.name} className="w-[669px]">
                  {/*eslint-disable-next-line @next/next/no-img-element*/}
                  <img src={f.signedUrl} alt={f.name} width="auto" />
                </div>
              ))
            )}
          </div>
        )
      ) : (
        <span className="font-normal text-base">No photos uploaded</span>
      )}
      <div className="max-w-[760px] flex flex-col md:flex-row justify-start md:justify-between items-start">
        <div className="w-full mt-3">
          <SectionHeading className="text-xl font-semibold">
            Documents ({documents.length})
          </SectionHeading>
          {documents.length > 0 ? (
            pipe(
              documents,
              A.map(f => (
                <div
                  className="w-full flex flex-row flex-wrap min-h-[80px] justify-start items-start gap-4 p-2 border-neutral-shade-18 border rounded mb-2"
                  key={f.id}
                >
                  <Icon name="file_blank_outline" className="text-2xl" />
                  <div className="ml-2 truncate">
                    <p className="text-sm font-semibold text-neutral-shade-100">
                      {f.displayName}
                    </p>
                    <p className="text-xs text-neutral-shade-58">
                      {[
                        f.size,
                        pipe(
                          f.category,
                          O.match(
                            () => null,
                            category => category
                          )
                        ),
                        pipe(
                          f.date,
                          O.getOrElse(() => "")
                        ),
                        pipe(
                          f.time,
                          O.getOrElse(() => "")
                        ),
                      ]
                        .filter(Boolean)
                        .join(" • ")}
                    </p>
                  </div>
                </div>
              ))
            )
          ) : (
            <span className="font-normal text-base">No documents uploaded</span>
          )}
        </div>
      </div>
    </GroupDiscussionSection>
  );
}
