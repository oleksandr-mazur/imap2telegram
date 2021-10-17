#!/bin/bash
set -e
export HELM_EXPERIMENTAL_OCI=1

if [ $(basename $(pwd)) == "tools" ]
then
    CHART_PATH="imap2telegram-helm"
else
    CHART_PATH="tools/imap2telegram-helm"
fi


IMAGE="ghcr.io/oleksandr-mazur/imap2telegram-helm"

# get git tag
TAG=$(git tag --points-at)
IMAGE_FULL="${IMAGE}:${TAG}"



case $1 in
    configure_helm)
        sed -i "s/^version:.*$/version: ${TAG}/" ${CHART_PATH}/Chart.yaml
        sed -i "s/^appVersion:.*$/appVersion: ${TAG}/" ${CHART_PATH}/Chart.yaml
        sed -i "s/^  tag:.*$/  tag: ${TAG}/" ${CHART_PATH}/values.yaml
    ;;
    helm_save)
        helm chart save ${CHART_PATH} ${IMAGE_FULL}
        helm chart list
    ;;
    helm_push)
        helm chart push "${IMAGE_FULL}"
    ;;
    *)
        echo -e "build_version|configure_helm"
    ;;
esac
