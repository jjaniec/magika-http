#!/bin/bash -xe

# ./k8s-service-account-kubeconfig.sh tooling service-account-name || echo ok
# mv kubeconfig ~/.kube/config

cd src
uvicorn main:app --host=0.0.0.0 --port=8080
