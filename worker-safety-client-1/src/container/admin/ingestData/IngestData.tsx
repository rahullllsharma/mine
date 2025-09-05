import type { IngestDataSelectOptionType } from "@/components/shared/inputSelect/InputSelect";
import type { UploadConfigs } from "@/components/upload/Upload";
import type { SelectOption } from "@/components/shared/select/Select";
import { useMutation, useQuery, useLazyQuery } from "@apollo/client";
import { useContext, useState, useEffect } from "react";
import { Icon } from "@urbint/silica";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import Upload from "@/components/upload/Upload";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import IngestOptions from "@/graphql/queries/IngestOptions.gql";
import IngestOptionItems from "@/graphql/queries/IngestOptionItems.gql";
import IngestCSV from "@/graphql/mutations/ingestData/IngestCSV.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import { CsvMetadata } from "./components/csvMetadata/CsvMetadata";
import { CsvItems } from "./components/csvItems/CsvItems";

type IngestOptionItems = {
  // `items` Will be an array of data matching the CSV columns
  // for the current ingest `selectedOption`
  items: Array<Record<string, unknown>>;
};
const configs: UploadConfigs = {
  title: "CSV",
  buttonLabel: "Add",
  buttonIcon: "file_blank_outline",
  allowedFormats: ".csv",
};

const delimiterOptions: Array<SelectOption> = [
  { id: ",", name: "," },
  { id: "|", name: "|" },
];

const IngestData = () => {
  const [ingestItems, setIngestItems] = useState([]);
  const [selectedOption, setSelectedOption] =
    useState<IngestDataSelectOptionType>();
  const [delimiterKey, setDelimiterKey] = useState(",");
  const toastCtx = useContext(ToastContext);

  const { data: { ingestOptions = { options: [] } } = {} } =
    useQuery(IngestOptions);

  const [uploadFile] = useMutation(IngestCSV, {
    onCompleted: ({ ingestCsv }) => {
      setIngestItems(ingestCsv.items);
      toastCtx?.pushToast("success", "Upload successful");
    },
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Error uploading data");
    },
  });

  const [getIngestionOptionItems, { loading, data }] = useLazyQuery(
    IngestOptionItems,
    {
      variables: { key: selectedOption?.id },
      onCompleted: ({ ingestOptionItems }) => {
        setIngestItems(ingestOptionItems.items);
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast("error", "Could not load ingest option");
      },
    }
  );

  useEffect(() => {
    if (selectedOption?.id) {
      getIngestionOptionItems();
    }
  }, [selectedOption?.id, data?.items, getIngestionOptionItems, loading]);

  const selectHandler = (option: IngestDataSelectOptionType) => {
    onSelect(option);
  };

  const uploadFileHandler = async (
    key: string,
    files: File[],
    delimiter: string
  ) => {
    if (!key) return;

    if (files.length !== 1) return;

    const file = files[0];

    const body = await file.text();
    uploadFile({
      variables: {
        key,
        body,
        delimiter,
      },
    });
  };

  const onSelect = async (option: IngestDataSelectOptionType) => {
    setSelectedOption(option);
  };

  return (
    <div className="h-screen overflow-y-auto">
      <section>
        <h2 className="text-xl font-semibold">Ingest Data</h2>

        <div className="mt-2">
          <FieldSearchSelect
            htmlFor="projectManager"
            label="Library"
            placeholder="Select a library type"
            icon="file_blank_outline"
            options={ingestOptions.options}
            onSelect={(option: SelectOption) =>
              selectHandler(option as IngestDataSelectOptionType)
            }
          />

          {selectedOption ? (
            <div className="mt-3">
              <Upload
                configs={{
                  ...configs,
                  title: selectedOption.name,
                  buttonLabel: `Upload ${selectedOption.name}`,
                }}
                onUpload={files =>
                  uploadFileHandler(selectedOption.id, files, delimiterKey)
                }
              />
              <p className="text-sm font-normal text-neutral-shade-75">
                <Icon name="warning_outline" className="mr-1" />
                {selectedOption.description}
              </p>
              <FieldSelect
                htmlFor="delimiter"
                label="Choose delimiter"
                placeholder=","
                options={delimiterOptions}
                onSelect={(option: SelectOption) =>
                  setDelimiterKey(String(option.id))
                }
                className="flex gap-3 mt-4"
              />
              <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
                Change the delimiter for ingest upload and copying data if
                commas occur in the dataset
              </div>
              <div className="responsive-padding-y">
                <CsvMetadata selectedOption={selectedOption} />
                <CsvItems
                  selectedOption={selectedOption}
                  items={ingestItems}
                  delimiter={delimiterKey}
                />
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
};

export { IngestData };
