import os
from pathlib import Path

import google.auth


def have_gcs_credentials() -> bool:
    gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gac is None or not Path(gac).exists():
        return False
    try:
        google.auth.default()  # type: ignore
    except google.auth.exceptions.DefaultCredentialsError:
        return False
    return True
