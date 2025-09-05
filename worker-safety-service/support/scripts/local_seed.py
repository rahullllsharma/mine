#!/usr/bin/env python3
# Exists only for backward compatibility.
# Can be run like:
#   poetry run ./support/scripts/local_seed.py
#   poetry run ./support/scripts/seed/main.py
# But please prefer:
#   poetry run seed

from support.scripts.seed import main

if __name__ == "__main__":
    main.app()
