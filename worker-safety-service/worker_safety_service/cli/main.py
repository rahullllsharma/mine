from worker_safety_service.cli.clustering import app as clustering_app
from worker_safety_service.cli.combined_scripts import app as combined_scripts_app
from worker_safety_service.cli.data_management.delete_ebos_in_date_range import (
    app as dm_ebos,
)
from worker_safety_service.cli.data_management.incidents import app as dm_incidents
from worker_safety_service.cli.data_management.migrate_tasks_to_activities import (
    app as data_management,
)
from worker_safety_service.cli.incidents import app as incident_app
from worker_safety_service.cli.ingest import app as ingest_app
from worker_safety_service.cli.library import app as library_app
from worker_safety_service.cli.open_api_spec import app as open_api_spec_app
from worker_safety_service.cli.pwc_maximo_integration import (
    app as pwc_maximo_integration_app,
)
from worker_safety_service.cli.risk_model import app as risk_model_app
from worker_safety_service.cli.tenant import app as tenant_app
from worker_safety_service.cli.users import app as users_app
from worker_safety_service.config import settings
from worker_safety_service.urbint_logging.fastapi_utils import TyperLogWrapper

data_management.add_typer(dm_incidents, name="incidents")
data_management.add_typer(dm_ebos, name="ebos")

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "cli"

app = TyperLogWrapper(with_sqlalchemy_stats=True)
app.add_typer(ingest_app, name="ingest")
app.add_typer(risk_model_app, name="risk-model")
app.add_typer(tenant_app, name="tenant")
app.add_typer(incident_app, name="incidents")
app.add_typer(users_app, name="users")
app.add_typer(combined_scripts_app, name="script")
app.add_typer(library_app, name="library")
app.add_typer(data_management, name="dm")
app.add_typer(clustering_app, name="clustering")
app.add_typer(pwc_maximo_integration_app, name="pwc-maximo")
app.add_typer(open_api_spec_app, name="rest-spec")

if __name__ == "__main__":
    app()
