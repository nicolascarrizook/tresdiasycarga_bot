# Sistema Mayra - n8n Workflows

Este directorio contiene todos los workflows de n8n para la automatización del Sistema Mayra, un sistema completo de generación automática de planes nutricionales.

## Estructura del Directorio

```
n8n_workflows/
├── README.md                           # Este archivo
├── patient_follow_up.json              # Seguimiento automático de pacientes
├── nutrition_plan_reminder.json        # Recordatorios de planes nutricionales
├── data_backup.json                    # Respaldo automático de datos
├── report_generation.json              # Generación de reportes periódicos
├── telegram_integration.json           # Integración con Telegram Bot
├── api_monitoring.json                 # Monitoreo de salud de APIs
├── templates/                          # Plantillas de workflows
│   ├── basic_webhook_template.json     # Plantilla básica de webhook
│   ├── scheduled_task_template.json    # Plantilla de tareas programadas
│   └── notification_template.json     # Plantilla de notificaciones
└── configs/                           # Archivos de configuración
    ├── n8n_settings.json              # Configuración principal de n8n
    ├── webhook_endpoints.json          # Definición de endpoints
    ├── environment_variables.env       # Variables de entorno
    └── docker-compose.yml              # Configuración de Docker
```

## Workflows Principales

### 1. Patient Follow-up Automation (`patient_follow_up.json`)

**Propósito:** Seguimiento automático de pacientes después de la entrega del plan nutricional.

**Características:**
- Ejecuta diariamente a las 8:00 AM
- Identifica pacientes que requieren seguimiento
- Envía mensajes personalizados según el tiempo transcurrido
- Diferencia entre check-ins (3 días), seguimientos semanales y mensuales
- Manejo de errores y logging

**Configuración:**
- Frecuencia: Diaria
- Horario: 08:00 AM (Argentina)
- Timeout: 2 minutos

### 2. Nutrition Plan Reminder (`nutrition_plan_reminder.json`)

**Propósito:** Recordatorios automáticos de comidas según el plan nutricional.

**Características:**
- Ejecuta 4 veces al día (8:00, 12:00, 16:00, 20:00)
- Obtiene la comida correspondiente del plan del paciente
- Envía recordatorios con detalles de preparación y macros
- Incluye botones interactivos para marcar como completado
- Opción para desactivar recordatorios

**Configuración:**
- Frecuencia: 4 veces al día
- Horarios: 08:00, 12:00, 16:00, 20:00
- Timezone: America/Argentina/Buenos_Aires

### 3. Data Backup (`data_backup.json`)

**Propósito:** Respaldo automático de todas las bases de datos del sistema.

**Características:**
- Ejecuta cada 6 horas
- Respalda PostgreSQL, ChromaDB, Redis y archivos de aplicación
- Subida a almacenamiento en la nube
- Limpieza automática de respaldos antiguos (>7 días)
- Notificaciones de éxito/error por Telegram

**Configuración:**
- Frecuencia: Cada 6 horas
- Retención: 7 días
- Ubicación: `/backups/`

### 4. Report Generation (`report_generation.json`)

**Propósito:** Generación automática de reportes semanales del sistema.

**Características:**
- Ejecuta los lunes a las 8:00 AM
- Recopila estadísticas de pacientes, planes y sistema
- Genera reportes en PDF
- Envía resúmenes por Telegram a admin y usuarios
- Métricas de rendimiento y uso

**Configuración:**
- Frecuencia: Semanal (lunes 8:00 AM)
- Formato: PDF + Telegram
- Métricas: Pacientes, planes, sistema, Telegram

### 5. Telegram Integration (`telegram_integration.json`)

**Propósito:** Integración completa con el bot de Telegram.

**Características:**
- Maneja webhooks de Telegram
- Procesa mensajes, comandos y callbacks
- Integra con los 3 motores del sistema
- Manejo de errores y logging
- Analytics y métricas

**Endpoints:**
- Webhook: `/webhook/telegram-webhook`
- Método: POST
- Autenticación: Ninguna (validación interna)

### 6. API Monitoring (`api_monitoring.json`)

**Propósito:** Monitoreo de salud de todos los servicios del sistema.

**Características:**
- Health checks cada 5 minutos
- Monitoreo de rendimiento cada hora
- Alertas críticas por Telegram
- Métricas de CPU, memoria, disco
- Tracking de tiempo de respuesta

**Servicios monitoreados:**
- FastAPI
- PostgreSQL
- Redis
- ChromaDB
- OpenAI
- Telegram Bot

## Plantillas de Workflows

### Basic Webhook Template
Plantilla básica para crear nuevos webhooks con:
- Procesamiento de datos
- Logging
- Respuesta estructurada

### Scheduled Task Template
Plantilla para tareas programadas con:
- Manejo de errores
- Logging de resultados
- Configuración de horarios

### Notification Template
Plantilla para notificaciones con:
- Diferentes tipos de alerta
- Formateo de mensajes
- Envío por Telegram

## Configuración

### Variables de Entorno Requeridas

```bash
# n8n Core
N8N_BASIC_AUTH_PASSWORD=your_password
N8N_DB_PASSWORD=your_db_password
N8N_JWT_SECRET=your_jwt_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_TELEGRAM_ID=your_admin_id

# OpenAI
OPENAI_API_KEY=your_openai_key

# Bases de datos
POSTGRES_PASSWORD=your_postgres_password
REDIS_PASSWORD=your_redis_password
```

### Configuración de n8n

1. **Configuración básica:**
   ```json
   {
     "timezone": "America/Argentina/Buenos_Aires",
     "locale": "es",
     "defaultExecutionTimeout": 300000
   }
   ```

2. **Configuración de webhook:**
   ```json
   {
     "webhook": {
       "baseUrl": "https://yourdomain.com/webhook",
       "testBaseUrl": "https://yourdomain.com/webhook-test"
     }
   }
   ```

## Instalación y Despliegue

### Usando Docker Compose

1. **Copiar archivo de configuración:**
   ```bash
   cp configs/environment_variables.env .env
   ```

2. **Configurar variables de entorno:**
   ```bash
   nano .env
   # Configurar todas las variables requeridas
   ```

3. **Iniciar servicios:**
   ```bash
   docker-compose -f configs/docker-compose.yml up -d
   ```

4. **Verificar estado:**
   ```bash
   docker-compose -f configs/docker-compose.yml ps
   ```

### Importar Workflows

1. **Acceder a n8n:**
   - URL: `http://localhost:5678`
   - Usuario: `admin`
   - Contraseña: (configurada en .env)

2. **Importar workflows:**
   - Ir a Templates > Import
   - Seleccionar cada archivo .json
   - Configurar credenciales
   - Activar workflows

### Configurar Webhooks

1. **Telegram Bot:**
   ```bash
   curl -X POST \
     "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://yourdomain.com/webhook/telegram-webhook"
     }'
   ```

2. **Verificar webhook:**
   ```bash
   curl -X GET \
     "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
   ```

## Monitoreo y Mantenimiento

### Health Checks

Cada workflow incluye verificaciones de salud:
- **API Health:** Cada 5 minutos
- **Performance:** Cada hora
- **Backups:** Cada 6 horas
- **Reports:** Semanal

### Logs

Los logs se almacenan en:
- **n8n logs:** `/var/log/n8n/`
- **Nginx logs:** `/var/log/nginx/`
- **Application logs:** Via API endpoints

### Métricas

Métricas disponibles:
- Ejecuciones de workflows
- Tiempo de respuesta
- Tasa de errores
- Uso de recursos

### Alertas

Sistema de alertas por Telegram:
- **Críticas:** Servicios caídos
- **Advertencias:** Rendimiento degradado
- **Información:** Respaldos completados

## Solución de Problemas

### Problemas Comunes

1. **Workflow no se ejecuta:**
   - Verificar que esté activo
   - Revisar logs de n8n
   - Comprobar configuración de timezone

2. **Webhook no recibe datos:**
   - Verificar URL del webhook
   - Comprobar configuración de red
   - Revisar logs de nginx

3. **Errores de base de datos:**
   - Verificar conexión a PostgreSQL
   - Comprobar credenciales
   - Revisar estado del contenedor

4. **Notificaciones no llegan:**
   - Verificar token de Telegram
   - Comprobar configuración de webhook
   - Revisar logs de API

### Debugging

1. **Habilitar debug:**
   ```bash
   export N8N_LOG_LEVEL=debug
   ```

2. **Revisar logs:**
   ```bash
   docker-compose logs -f n8n
   ```

3. **Verificar conectividad:**
   ```bash
   docker-compose exec n8n ping api
   ```

## Seguridad

### Autenticación

- **n8n Admin:** Autenticación básica
- **Webhooks:** Validación de payload
- **API:** JWT tokens
- **Base de datos:** Credenciales seguras

### Configuración de Seguridad

1. **Usar HTTPS:**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/ssl/certs/cert.pem;
       ssl_certificate_key /etc/ssl/private/key.pem;
   }
   ```

2. **Rate limiting:**
   ```json
   {
     "rate_limiting": {
       "max_requests_per_minute": 60,
       "max_requests_per_hour": 1000
     }
   }
   ```

3. **IP Whitelisting:**
   ```json
   {
     "ip_whitelist": {
       "enabled": true,
       "allowed_ips": ["127.0.0.1", "::1"]
     }
   }
   ```

## Extensibilidad

### Crear Nuevos Workflows

1. **Usar plantillas:**
   - Copiar template apropiado
   - Modificar según necesidades
   - Configurar triggers y acciones

2. **Mejores prácticas:**
   - Incluir manejo de errores
   - Agregar logging apropiado
   - Configurar timeouts
   - Documentar workflow

### Integrar Nuevos Servicios

1. **Agregar configuración:**
   ```json
   {
     "new_service": {
       "url": "http://service:port",
       "timeout": 5000,
       "critical": true
     }
   }
   ```

2. **Actualizar monitoreo:**
   - Agregar health check
   - Configurar alertas
   - Incluir en reportes

## Contribución

### Desarrollo Local

1. **Clonar repositorio:**
   ```bash
   git clone <repository>
   cd n8n_workflows
   ```

2. **Configurar entorno:**
   ```bash
   cp configs/environment_variables.env .env
   # Configurar variables locales
   ```

3. **Ejecutar en desarrollo:**
   ```bash
   docker-compose -f configs/docker-compose.yml up -d
   ```

### Lineamientos

- Usar nombres descriptivos para workflows
- Incluir documentación en cada nodo
- Manejar errores apropiadamente
- Seguir convenciones de nomenclatura
- Probar workflows antes de producción

## Soporte

Para soporte técnico:
- **Documentación:** Esta guía
- **Logs:** `/var/log/n8n/`
- **Monitoreo:** Grafana dashboard
- **Alertas:** Canal de Telegram

## Licencia

Este proyecto es parte del Sistema Mayra y está sujeto a sus términos de licencia.

---

**Última actualización:** 2024-01-15
**Versión:** 1.0
**Autor:** Sistema Mayra Development Team