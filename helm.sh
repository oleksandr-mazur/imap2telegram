#!/bin/bash

TAG=$(git tag --points-at)
cd pages

CHART_PATH="../chart"

# sed -i "s/^version:.*$/version: ${TAG}/" ${CHART_PATH}/Chart.yaml
# sed -i "s/^appVersion:.*$/appVersion: ${TAG}/" ${CHART_PATH}/Chart.yaml
sed -i "s/^  tag:.*$/  tag: ${TAG}/" ${CHART_PATH}/values.yaml

helm package --version ${TAG} --app-version ${TAG} ${CHART_PATH}

helm repo index --url https://oleksandr-mazur.github.io/imap2telegram/packages/ --merge index.yaml .

