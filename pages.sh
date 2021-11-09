#!/bin/bash

TAG=$(git tag --points-at)
APP_VERSION=$TAG

if [ -z $TAG ]
then
    TAG="latest"
fi

test -d helm || mkdir helm
cd helm

CHART_PATH="../chart"

# sed -i "s/^version:.*$/version: ${TAG}/" ${CHART_PATH}/Chart.yaml
# sed -i "s/^appVersion:.*$/appVersion: ${TAG}/" ${CHART_PATH}/Chart.yaml
sed -i "s/^  tag:.*$/  tag: ${TAG}/" ${CHART_PATH}/values.yaml

if [ "$TAG" == "latest" ]
then
    helm package ${CHART_PATH}
else
    helm package --version ${APP_VERSION} --app-version ${APP_VERSION} ${CHART_PATH}
fi

helm repo index --url https://oleksandr-mazur.github.io/imap2telegram/helm/ --merge index.yaml .

