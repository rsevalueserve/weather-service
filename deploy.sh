#!/bin/bash
set -e

NAMESPACE=${1:-dev}

minikube kubectl -- apply -f k8s/namespace-$NAMESPACE.yaml || true
minikube kubectl -- -n $NAMESPACE apply -f k8s/configmap.yaml
minikube kubectl -- -n $NAMESPACE apply -f k8s/secret.yaml
minikube kubectl -- -n $NAMESPACE apply -f k8s/deployment.yaml
minikube kubectl -- -n $NAMESPACE apply -f k8s/service.yaml
minikube kubectl -- -n $NAMESPACE apply -f k8s/hpa.yaml
minikube kubectl -- -n $NAMESPACE apply -f k8s/ingress.yaml

echo "Despliegue completado en el namespace $NAMESPACE."
