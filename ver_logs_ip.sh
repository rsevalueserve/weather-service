#!/bin/bash
# Script para ver los últimos logs de IP dentro del pod del microservicio
# Uso: ./ver_logs_ip.sh [namespace]

NAMESPACE=${1:-dev}
# Usa 'minikube kubectl --' para pasar correctamente los flags a kubectl
POD=$(minikube kubectl -- get pods -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | grep weather | head -n1)

if [ -z "$POD" ]; then
  echo "No se encontró un pod que contenga 'weather' en el nombre en el namespace $NAMESPACE."
  echo "Puedes ajustar el filtro en este script si tu pod tiene otro nombre."
  exit 1
fi

minikube kubectl -- exec -n $NAMESPACE $POD -- tail -20 /tmp/ip_debug.log
