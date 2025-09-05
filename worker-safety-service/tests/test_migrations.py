# type: ignore

import importlib.util
import os

HERE = os.path.abspath(os.path.dirname(__file__))
MIGRATIONS_PATH = os.path.join(os.path.dirname(HERE), "migrations", "versions")


def test_migrations_references() -> None:
    # Grab versions
    revisions = []
    valid_revisions = set()
    for filename in os.listdir(MIGRATIONS_PATH):
        if filename.endswith(".py"):
            path = os.path.join(MIGRATIONS_PATH, filename)
            spec = importlib.util.spec_from_file_location("wss_migrations", path)
            version = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version)
            assert not version.down_revision or isinstance(
                version.down_revision, str
            ), "no merges allowed"
            revisions.append((version.down_revision, filename))
            valid_revisions.add(version.revision)

    # Validate
    existing_down_revisions = {}
    for down_revision, filename in revisions:
        if down_revision:
            assert (
                down_revision in valid_revisions
            ), f"Down revision {down_revision} not found. File:{filename}"
        assert (
            down_revision not in existing_down_revisions
        ), f"Down revision {down_revision} on {filename} already defined in {existing_down_revisions[down_revision]}"
        existing_down_revisions[down_revision] = filename
