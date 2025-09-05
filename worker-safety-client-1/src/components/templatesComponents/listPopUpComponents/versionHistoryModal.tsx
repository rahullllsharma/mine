import type {
  TemplatesList,
  TemplatesListRequest,
} from "../customisedForm.types";
import React, { useContext, useEffect, useMemo, useState } from "react";
import axiosRest from "../../../api/customFlowApi";
import useRestMutation from "../../../hooks/useRestMutation";
import { messages } from "../../../locales/messages";
import EmptyContent from "../../emptyContent/EmptyContent";
import Modal from "../../shared/modal/Modal";
import ToastContext from "../../shared/toast/context/ToastContext";
import { VersionHistoryList } from "../listView/VersionHistoryList";
import Loader from "../../shared/loader/Loader";

type VersionHistoryModalProps = {
  isOpen: boolean;
  onClose: () => void;
  publishedTemplateUUID: string;
  selectedTemplateTitle: string;
};

const GET_VERSION_HISTORY_LIST_LIMIT = 10;

const VersionHistoryModal = ({
  isOpen,
  onClose,
  publishedTemplateUUID,
  selectedTemplateTitle,
}: VersionHistoryModalProps) => {
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [disableFetchMore, setDisableFetchMore] = useState(false);
  const [publishedVersionHistoryList, setPublishedVersionHistoryList] =
    useState<TemplatesList[]>([]);

  const toastCtx = useContext(ToastContext);

  const uiState = useMemo(() => {
    return loading ? "loading" : undefined;
  }, [loading]);

  const { mutate: fetchVersionHistoryList } = useRestMutation<any>({
    endpoint: "/templates/history/",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onSuccess: (responseData: any) => {
        setPublishedVersionHistoryList(prevList =>
          offset === 0
            ? responseData.data.data
            : [...prevList, ...responseData.data.data]
        );

        setLoading(false);
        setOffset(offset + GET_VERSION_HISTORY_LIST_LIMIT);
        setDisableFetchMore(
          responseData.data.data.length < GET_VERSION_HISTORY_LIST_LIMIT
        );
      },
      onError: () => {
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
    },
  });

  const fetchData = async () => {
    try {
      const requestPayload: TemplatesListRequest = {
        template_unique_id: publishedTemplateUUID,
        limit: GET_VERSION_HISTORY_LIST_LIMIT,
        offset,
        orderBy: {
          field: "published_at",
          desc: true,
        },
        title: selectedTemplateTitle,
      };
      setLoading(true);
      fetchVersionHistoryList(requestPayload);
    } catch (err) {
      toastCtx?.pushToast("error", messages.ErrorFetchingTemplatesList);
      setLoading(false);
    }
  };

  const onLoadMoreTemplatesList = () => {
    if (disableFetchMore) return; // Exit early if fetch more is disabled
    fetchData(); // Call fetchData to fetch more data
  };

  // Initialize data fetching when component mounts
  useEffect(() => {
    setOffset(0);
    if (isOpen === true) {
      fetchData();
    }
  }, [isOpen]);

  return (
    <Modal
      className="!max-w-[50rem] bg-[#f7f8f8]"
      title="Version History"
      isOpen={isOpen}
      closeModal={onClose}
    >
      {(() => {
        if (publishedVersionHistoryList?.length > 0) {
          return (
            <VersionHistoryList
              listData={publishedVersionHistoryList}
              state={uiState}
              disableFetchMore={disableFetchMore}
              onView={id => {
                id;
              }}
              onLoadMore={() => onLoadMoreTemplatesList()}
            />
          );
        } else {
          if (!loading) {
            return (
              <EmptyContent
                title="No Templates Found"
                description="If you believe this is an error, please contact your customer success manager to help troubleshoot the issues."
              />
            );
          } else {
            return <Loader />;
          }
        }
      })()}
    </Modal>
  );
};

export default VersionHistoryModal;
