#!/bin/bash
set -x
set -e


REGISTRY="ghcr.io/oleksandr-mazur/imap2telegram-helm"

echo "$GITHUB_TOKEN" | helm registry login -u $GITHUB_TOKEN --password-stdin $REGISTRY

./utils.sh configure_helm

./utils.sh helm_save
./utils.sh helm_push

helm registry logout $REGISTRY

