# Docker Configuration for Sistema Mayra

This directory contains all Docker-related configuration files for the Sistema Mayra project.

## Directory Structure

```
docker/
   api/
      Dockerfile          # API service container
   telegram_bot/
      Dockerfile          # Telegram bot service container
   nginx/
      Dockerfile          # Nginx reverse proxy container
      nginx.conf          # Main nginx configuration
      conf.d/
          default.conf    # Default site configuration
   postgres/
      init.sql           # Database initialization script
   README.md              # This file
```

## Quick Start

### Development Environment

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your actual values, especially:
   - `TELEGRAM_BOT_TOKEN`
   - `POSTGRES_PASSWORD`
   - `REDIS_PASSWORD`
   - `SECRET_KEY`

3. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. Access the services:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PGAdmin: http://localhost:5050
   - Nginx: http://localhost:80

### Production Environment

1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. Generate SSL certificates (if using HTTPS):
   ```bash
   mkdir ssl
   # Add your SSL certificates to the ssl/ directory
   ```

3. Start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. For monitoring (optional):
   ```bash
   docker-compose -f docker-compose.prod.yml --profile monitoring up -d
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `secure_password_123` |
| `REDIS_PASSWORD` | Redis password | `redis_password_123` |
| `SECRET_KEY` | Application secret key | `super-secret-key-for-jwt-tokens` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `mayra_db` |
| `POSTGRES_USER` | Database user | `postgres` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Services

### API Service
- **Port**: 8000
- **Health Check**: `/health`
- **Documentation**: `/docs`
- **Dependencies**: PostgreSQL, Redis

### Telegram Bot Service
- **Dependencies**: API, PostgreSQL, Redis
- **Purpose**: Handles Telegram bot interactions

### Nginx Service
- **Port**: 80 (dev), 80/443 (prod)
- **Purpose**: Reverse proxy and load balancer
- **Features**: Rate limiting, SSL termination, static file serving

### Database Service
- **Port**: 5432
- **Type**: PostgreSQL 15
- **Persistence**: Named volumes

### Redis Service
- **Port**: 6379
- **Purpose**: Caching and session storage
- **Persistence**: Named volumes

## Monitoring (Production Only)

### Prometheus
- **Port**: 9090
- **Purpose**: Metrics collection
- **Profile**: `monitoring`

### Grafana
- **Port**: 3000
- **Purpose**: Metrics visualization
- **Profile**: `monitoring`

## Maintenance Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f api
```

### Database Backup
```bash
# Create backup
docker exec mayra_db_dev pg_dump -U postgres mayra_db > backup.sql

# Restore backup
docker exec -i mayra_db_dev psql -U postgres mayra_db < backup.sql
```

### Scale Services (Production)
```bash
# Scale API service
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Update Services
```bash
# Rebuild and restart services
docker-compose -f docker-compose.dev.yml up -d --build
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database Passwords**: Use strong, unique passwords
3. **SSL Certificates**: Use valid SSL certificates in production
4. **Network Security**: Services communicate through internal networks
5. **User Privileges**: Containers run as non-root users

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 80, 5432, 6379, 8000 are available
2. **Permission Errors**: Check file permissions and user ownership
3. **Database Connection**: Verify database credentials and network connectivity
4. **Bot Token**: Ensure Telegram bot token is valid and properly formatted

### Debug Commands

```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# View resource usage
docker stats

# Access service shell
docker exec -it mayra_api_dev /bin/bash

# Check network connectivity
docker exec mayra_api_dev ping db
```

## Development Tips

1. Use `docker-compose.dev.yml` for development
2. Enable volume mounts for hot reloading
3. Use PGAdmin for database management
4. Monitor logs during development
5. Use health checks to ensure service reliability

## Production Tips

1. Use `docker-compose.prod.yml` for production
2. Enable monitoring with Prometheus and Grafana
3. Set up log aggregation
4. Use environment-specific configurations
5. Implement proper backup strategies
6. Monitor resource usage and scale accordingly