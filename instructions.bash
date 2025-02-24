sudo snap install google-cloud-cli --classic
gcloud init
gcloud auth application-default login
gcloud auth print-access-token # I don't think we need this...
export GOOGLE_CLOUD_QUOTA_PROJECT="sigma-icon-451605-s6"
gcloud auth application-default set-quota-project sigma-icon-451605-s6