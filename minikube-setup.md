

# Configuración del entorno para Minikube

Este documento describe los pasos para validar y preparar tu sistema Linux para ejecutar Minikube, incluyendo la configuración de cgroup2, que es requerida por las versiones modernas de Kubernetes y contenedores.

## 1. Validar soporte para virtualización y cgroup2

### a) Verificar soporte de virtualización

```bash
lscpu | grep Virtualization
```

Debe mostrar una línea con `VT-x` (Intel) o `AMD-V` (AMD). Si no aparece, revisa la configuración de tu BIOS/UEFI.

### b) Verificar cgroup2

Para comprobar si el sistema está usando cgroup2:

```bash
mount | grep cgroup2
```

Debe aparecer una línea similar a:

```
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime)
```

## 2. Habilitar cgroup2 (si es necesario)

Si tu sistema no está usando cgroup2, puedes habilitarlo agregando el siguiente parámetro al kernel:

1. Edita el archivo de configuración de GRUB:
   ```bash
   sudo nano /etc/default/grub
   ```
2. Busca la línea que comienza con `GRUB_CMDLINE_LINUX_DEFAULT` y agrega:
   ```
   systemd.unified_cgroup_hierarchy=1
   ```
   Ejemplo:
   ```
   GRUB_CMDLINE_LINUX_DEFAULT="quiet splash systemd.unified_cgroup_hierarchy=1"
   ```
3. Actualiza GRUB y reinicia:
   ```bash
   sudo update-grub
   sudo reboot
   ```
4. Tras reiniciar, valida nuevamente con:
   ```bash
   mount | grep cgroup2
   ```

## 3. Instalar Minikube y dependencias

- [Guía oficial de instalación de Minikube](https://minikube.sigs.k8s.io/docs/start/)
- Instala también kubectl y Docker si no los tienes.

## 4. Iniciar Minikube

```bash
minikube start --driver=docker --extra-config=kubelet.cgroup-driver=systemd
```

Si todo está correcto, Minikube iniciará un clúster local listo para pruebas.

---
# Requisitos previos y addons recomendados para Minikube

Antes de iniciar, asegúrate de cumplir con los siguientes requisitos y de tener habilitados los addons necesarios para las pruebas y despliegue de microservicios en Minikube:

## Requisitos previos
- Linux con soporte de virtualización (VT-x/AMD-V)
- Docker instalado y funcionando
- kubectl instalado
- Minikube instalado

## Addons de Minikube activados en las pruebas

Para el correcto funcionamiento de los despliegues y pruebas, se recomienda habilitar los siguientes addons:

- **ingress**: Para exponer servicios vía dominios locales y simular un entorno real.
  ```bash
  minikube addons enable ingress
  ```
- **metrics-server**: Para habilitar el autoscalado (HPA) y la recolección de métricas de recursos.
  ```bash
  minikube addons enable metrics-server
  ```
- **dashboard**: (Opcional, pero recomendado) Para visualizar y gestionar recursos de Kubernetes vía interfaz web.
  ```bash
  minikube addons enable dashboard
  ```
- **default-storageclass** y **storage-provisioner**: Generalmente habilitados por defecto, permiten el aprovisionamiento dinámico de volúmenes persistentes.

Puedes ver el estado de los addons con:
```bash
minikube addons list
```

---

## Despliegue y pruebas en Minikube

### 1. Desplegar recursos Kubernetes

Puedes usar el script:

```bash
./deploy.sh dev
```

O manualmente:

```bash
kubectl apply -f k8s/namespace-dev.yaml
kubectl -n dev apply -f k8s/configmap.yaml
kubectl -n dev apply -f k8s/secret.yaml
kubectl -n dev apply -f k8s/deployment.yaml
kubectl -n dev apply -f k8s/service.yaml
kubectl -n dev apply -f k8s/hpa.yaml
kubectl -n dev apply -f k8s/ingress.yaml
```

### 2. Acceso al servicio

- Habilita Ingress:

```bash
minikube addons enable ingress
```

- Agrega a `/etc/hosts`:
```
127.0.0.1 weather.local
```
- Accede a `http://weather.local/api/v1/clima-info`

O usa NodePort:

```bash
minikube service -n dev weather-api
```

O port-forward:

```bash
kubectl -n dev port-forward svc/weather-api 8000:8000
```

### 3. Simular carga y ver logs

- Simular carga:

```bash
ab -n 2000 -c 100 http://weather.local/api/v1/clima-info
```

- Ver logs:

```bash
kubectl -n dev logs -l app=weather-api
```

### 4. Escalado

- Manual:
```bash
kubectl -n dev scale deployment weather-api --replicas=2
```
- Automático: El HPA escalará según uso de CPU.

---

# Pruebas de autoscalado (HPA) en Minikube

Todas las pruebas de autoscalado están pensadas y validadas específicamente para Minikube. Asegúrate de tener el clúster Minikube corriendo y el namespace correcto (`dev`).

## 1. Verifica el estado del HPA

```bash
minikube kubectl -- -n dev get hpa
```

## 2. Genera carga sobre el servicio

Puedes usar Apache Benchmark (ab) para simular carga:

```bash
ab -n 5000 -c 200 http://weather.local/api/v1/clima-info
```

O si usas port-forward:

```bash
ab -n 5000 -c 200 http://localhost:8000/api/v1/clima-info
```

## 3. Observa el escalado

En otra terminal, monitorea el HPA y los pods:

```bash
minikube kubectl -- -n dev get hpa
minikube kubectl -- -n dev get pods
```

Verás cómo el HPA incrementa el número de réplicas si el uso de CPU supera el umbral configurado.

## 4. Verifica métricas y detalles

```bash
minikube kubectl -- -n dev describe hpa
```

> Recuerda: El autoscalado puede tardar unos minutos en reflejarse según la carga y la configuración del HPA.

---

## Ejemplo de resultados esperados de autoscalado (HPA)

A continuación se muestran ejemplos reales de lo que deberías observar si el HPA está funcionando correctamente tras generar carga:

### Estado inicial del HPA

```
NAME          REFERENCE                TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
weather-api   Deployment/weather-api   5%/50%    1         5         1          2m
```

### Durante la carga (el HPA escala)

```
NAME          REFERENCE                TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
weather-api   Deployment/weather-api   80%/50%   1         5         3          4m
```

### Estado de los pods

```
NAME                          READY   STATUS    RESTARTS   AGE
weather-api-xxxxxxx-xxxxx     1/1     Running   0          4m
weather-api-xxxxxxx-yyyyy     1/1     Running   0          1m
weather-api-xxxxxxx-zzzzz     1/1     Running   0          1m
```

### Eventos del HPA

```
Events:
  Type    Reason             Age   From                       Message
  ----    ------             ----  ----                       -------
  Normal  SuccessfulRescale  1m    horizontal-pod-autoscaler  New size: 3; reason: cpu resource utilization (percentage of request) above target
```

Puedes monitorear el escalado en tiempo real con:

```bash
watch -n 2 "minikube kubectl -- -n dev get hpa,pods"
```

---

## Troubleshooting: IP privada en clúster y solución

### Problema

Al desplegar el microservicio en Minikube/Kubernetes, la obtención de la IP del cliente desde el endpoint `/clima-info` puede devolver una IP privada (por ejemplo, `10.x.x.x`, `192.168.x.x`, `127.0.0.1` o `::1`). Esto causa que la geolocalización y la consulta climática fallen o den resultados incorrectos, ya que los servicios externos requieren una IP pública real.

### Solución implementada

- Se añadió lógica en el endpoint para detectar si la IP recibida es privada.
- Si la IP es privada, se obtiene la IP pública real del pod usando `https://api.ipify.org`.
- Se registran logs detallados (stdout y `/tmp/ip_debug.log`) para depuración y troubleshooting.
- Se provee un script automático (`ver_logs_ip.sh`) para consultar los logs de IP dentro del pod en Minikube:

```bash
./ver_logs_ip.sh dev
```

El script detecta automáticamente el pod y muestra los últimos logs relevantes.

### Ejemplo de logs

```
IP recibida en request: 10.244.0.42
La IP detectada es privada, se intentará obtener la IP pública real...
IP pública obtenida: 181.XX.XX.XX
```

### Recomendaciones

- Siempre revisar los logs si la geolocalización/clima no funciona como se espera.
- Si cambias el nombre del pod, ajusta el filtro en el script.
- Documenta cualquier cambio adicional en este archivo.

---

# Buenas prácticas para logs en producción

- Mantén solo los logs necesarios para troubleshooting y auditoría:
  - Entrada de request (IP recibida, endpoint invocado).
  - Errores y excepciones (con detalles suficientes para depurar).
  - Acciones relevantes (por ejemplo, si se usó IP pública o privada).
- Evita loguear bodies completos de respuestas externas y claves API.
- Usa logs de nivel INFO para eventos normales y ERROR/EXCEPTION para fallos.
- El script `ver_logs_ip.sh` permite consultar logs de IP en el pod de forma sencilla.

# Ejemplo de logs recomendados

```
INFO  IP recibida en request: 10.244.0.42
INFO  La IP detectada es privada, se intentará obtener la IP pública real...
INFO  IP pública obtenida: 181.XX.XX.XX
ERROR Error de OpenWeatherMap: city not found
EXCEPTION Error consultando ip-api.com para 10.244.0.42: ...
```


---

# Resumen de organización, archivos clave y decisiones técnicas

Este proyecto implementa un microservicio de información climática y geográfica, preparado para despliegue moderno en Kubernetes (Minikube). A continuación se resumen los principales componentes, su propósito y las decisiones técnicas que garantizan seguridad, escalabilidad, observabilidad y buenas prácticas DevOps.

## Tabla resumen de archivos clave

| Archivo/Carpeta                | Propósito                                                      |
|--------------------------------|----------------------------------------------------------------|
| Dockerfile                     | Build de la imagen del microservicio                           |
| k8s/deployment.yaml            | Despliegue del pod en Kubernetes                               |
| k8s/service.yaml               | Exposición del servicio en el clúster                          |
| k8s/configmap.yaml             | Configuración no sensible (variables de entorno)                |
| k8s/secret.yaml                | Configuración sensible (API keys, secretos)                     |
| k8s/hpa.yaml                   | Configuración de escalado automático (HPA)                      |
| k8s/ingress.yaml               | Ingress para acceso externo (opcional)                          |
| k8s/namespace-dev.yaml         | Namespace para entorno de desarrollo                            |
| k8s/namespace-prod.yaml        | Namespace para entorno de producción                            |
| deploy.sh                      | Script para automatizar despliegue                              |
| minikube-setup.md              | Guía de despliegue y troubleshooting en Minikube                |
| README.md                      | Documentación general y arquitectura                            |
| app/api/v1/endpoints.py        | Endpoint principal `/clima-info`                                |
| app/infrastructure/ipinfo_api.py| Adapter para geolocalización por IP                             |
| app/infrastructure/weather_api.py| Adapter para consulta de clima                                 |
| .gitignore                     | Exclusión de archivos temporales y sensibles del repositorio     |

## Decisiones técnicas y justificación

| Decisión / Práctica                    | Justificación                                                                                 |
|----------------------------------------|----------------------------------------------------------------------------------------------|
| Uso de Minikube                        | Permite simular un entorno real de Kubernetes en local, ideal para pruebas y desarrollo       |
| Separación de entornos (namespaces)     | Facilita pruebas independientes y control de recursos entre dev/prod                          |
| ConfigMap y Secret                     | Mantiene la configuración desacoplada y segura, siguiendo buenas prácticas                    |
| Probes (readiness/liveness)            | Garantizan la disponibilidad y salud del servicio                                             |
| HPA y escalado manual                  | Permiten escalar el servicio según demanda y simular escenarios de carga                      |
| Logs estructurados y troubleshooting    | Facilitan la auditoría y el diagnóstico de problemas en producción y desarrollo               |
| Documentación y scripts automáticos     | Mejoran la reproducibilidad y la experiencia de onboarding                                    |
| .gitignore para logs y secretos         | Evita exponer información sensible o irrelevante en el repositorio                            |
| Diagrama de arquitectura (Mermaid)      | Claridad visual sobre el flujo y componentes del sistema                                      |

---

## Evidencia y explicación del autoscalado (HPA)

Durante las pruebas, se ajustó el umbral de CPU del HPA para forzar y observar el escalado automático:

- **Umbral configurado:**
  - Inicialmente: 70%
  - Pruebas de escalado: 10%, luego 3% (para forzar el escalado)
  - Valor final recomendado/documentado: **20%**

- **Evidencia de escalado exitoso:**

```bash
minikube kubectl -- -n dev get hpa
NAME              REFERENCE                TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
weather-api-hpa   Deployment/weather-api   cpu: 35%/3%   1         3         3          5h16m

minikube kubectl -- -n dev get pods
NAME                           READY   STATUS    RESTARTS   AGE
weather-api-7b8b88fc7f-6ksq5   1/1     Running   0          35s
weather-api-7b8b88fc7f-845nc   1/1     Running   0          5m14s
weather-api-7b8b88fc7f-w6k7q   1/1     Running   0          35s

minikube kubectl -- -n dev describe hpa weather-api-hpa
...
Metrics: ( current / target )
  resource cpu on pods  (as a percentage of request):  35% (35m) / 3%
...
Events:
  Normal   SuccessfulRescale        45s   horizontal-pod-autoscaler  New size: 3; reason: cpu resource utilization (percentage of request) above target
```

- **Explicación:**
  - El HPA escaló el número de réplicas automáticamente al superar el umbral configurado.
  - El valor final recomendado de umbral de CPU es **20%**, que permite observar el escalado bajo cargas moderadas y es adecuado para entornos de prueba.
  - Puedes ajustar este valor según la demanda real de tu microservicio en producción.

---

**Nota sobre el umbral de autoscalado:**

Para facilitar y acelerar la observación del autoscalado durante las pruebas en Minikube, el umbral de CPU del HPA se ha configurado en **20%** (en lugar de valores más altos como 50% o 70%). Esto permite que el escalado ocurra rápidamente bajo cargas moderadas y es ideal para entornos de laboratorio o demostración. En producción, ajusta este valor según el comportamiento real y la demanda del microservicio.

---