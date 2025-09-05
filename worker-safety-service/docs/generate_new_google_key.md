# Google local-dev Service Account
We have a [Service Account]() for GCP resources used in local development.

### Creating a credentials file
Follow these steps to create a new credentials file.
```bash
brew install --casks google-cloud-sdk

gcloud auth login
gcloud iam service-accounts keys create .google-dev-service-account.json --iam-account=worker-safety-local-dev@urbint-1259.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/.google-dev-service-account.json
```
