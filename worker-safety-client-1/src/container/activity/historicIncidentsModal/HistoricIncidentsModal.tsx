import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { Incident } from "@/types/project/Incident";
import cx from "classnames";
import { useQuery } from "@apollo/client";
import Modal from "@/components/shared/modal/Modal";
import { messages } from "@/locales/messages";
import Loader from "@/components/shared/loader/Loader";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import { IncidentCard } from "@/components/incidentCard/IncidentCard";
import getHistoricIncidents from "@/graphql/queries/getHistoricIncidents.gql";
import { convertDateToString } from "@/utils/date/helper";
import EmptyIncidents from "@/components/incidentCard/EmptyIncidents";
import { SeverityValues } from "./Severity";

type HistoricIncidentsModalProps = {
  task: TaskHazardAggregator;
  onModalClose: () => void;
  className?: string;
};

function HistoricIncidentsModal({
  task,
  onModalClose,
  className,
}: HistoricIncidentsModalProps) {
  const { name, libraryTask } = task;
  const libraryTaskId = libraryTask?.id;
  const { data, loading } = useQuery(getHistoricIncidents, {
    variables: { libraryTaskId: libraryTaskId },
  });

  if (loading) return <Loader />;

  const incidents: Incident[] = data.historicalIncidents;

  return (
    <Modal
      isOpen
      title={messages.historicIncidentModalTitle}
      subtitle={name}
      closeModal={onModalClose}
      className={cx("max-h-[80vh] overflow-y-auto", className)}
    >
      {incidents.length === 0 ? (
        <EmptyIncidents />
      ) : (
        incidents.map(
          ({ id, description, incidentDate, incidentType, severity }) => (
            <IncidentCard
              key={id}
              title={incidentType}
              severity={SeverityValues[severity]}
              description={description}
              date={convertDateToString(incidentDate)}
              className="mb-4 last:mb-0"
            />
          )
        )
      )}
      <footer className="flex flex-1 justify-end">
        <ButtonRegular label="Close" onClick={onModalClose} />
      </footer>
    </Modal>
  );
}

export { HistoricIncidentsModal };
