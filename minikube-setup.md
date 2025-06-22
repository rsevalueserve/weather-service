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
ab -n 100 -c 10 http://weather.local/api/v1/clima-info
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