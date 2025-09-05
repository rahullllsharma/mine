# Cloud SQL Backup Action

---

This GitHub Action automates the process of taking backups of a specified Google Cloud SQL instance across different environments.

---

## Inputs

* **`environment`** (Required)
    * **Options:** `integ`, `staging`, `prod`
    * **Description:** This input helps categorize and manage backups based on the environment.

* **`cloudsql_instance`** (Required)
    * **Description:** The specific instance you want to create a backup for (e.g., `my-database-instance`).

* **`cloudsql_backup_description`** (Required)
    * **Description:** This helps identify the backup later (e.g., `Daily backup before deployment`).

---

## How It Works

This action performs the following steps:

1.  **Authentication**: Authenticates with Google Cloud using provided credentials.
2.  **GCP CLI Setup**: Sets up the Google Cloud CLI environment.
3.  **Backup Creation**: Executes the `gcloud sql backups create` command to initiate a backup of the specified Cloud SQL instance with the provided description.

---

## Usage Example

```yaml
name: Manual Cloud SQL Backup

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment (integ, staging, prod)'
        required: true
        type: choice
        options:
          - integ
          - staging
          - prod
      cloudsql_instance:
        description: 'Name of the Cloud SQL instance to backup'
        required: true
        type: string
      cloudsql_backup_description:
        description: 'Description of the Cloud SQL backup'
        required: true
        type: string

jobs:
  backup:
    runs-on: ubuntu-latest
    env:
      CREDENTIALS_JSON: ${{ secrets.GCP_CREDENTIALS_JSON }}
      GCP_PROJECT_ID: your-gcp-project-id # Replace with your actual GCP Project ID
    steps:
      - name: 'Cloud SQL Backup'
        uses: './.github/actions/cloud-sql-backup' # Path to your action
        with:
          environment: ${{ github.event.inputs.environment }}
          cloudsql_instance: ${{ github.event.inputs.cloudsql_instance }}
          cloudsql_backup_description: ${{ github.event.inputs.cloudsql_backup_description }}
```

## Setup
* **GCP Credentials**: Ensure you have a service account key with the necessary permissions to create Cloud SQL backups. Store this JSON key as a GitHub secret (e.g., GCP_CREDENTIALS_JSON).
* **GCP Project ID**: Set your Google Cloud Project ID as an environment variable in your workflow (e.g., GCP_PROJECT_ID).
Action Path: If this action is located within your repository, update the uses path accordingly (e.g., ./.github/actions/cloud-sql-backup).