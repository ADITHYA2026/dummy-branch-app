# Branch Loan API - Production Ready

A containerized Flask microloans API with automated CI/CD pipelines and multi-environment support.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Flask API     │    │  PostgreSQL     │
│                 │    │                 │    │                 │
│ - HTTPS Term    │◄──►│ - REST API      │◄──►│ - Database      │
│ - SSL Certs     │    │ - Business Logic│    │ - Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                        │                       │
       │ 80/443                 │ 8000                  │ 5432
       ▼                        ▼                       ▼
  External Users           Internal                 Data Storage
                          Communication
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenSSL (for certificate generation)

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/dummy-branch-app
   cd dummy-branch-app
   ```

2. **Generate SSL certificates**
   ```bash
   mkdir -p ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/branchloans.com.key \
     -out ssl/branchloans.com.crt \
     -subj "/C=US/ST=State/L=City/O=Organization/CN=branchloans.com"
   ```

3. **Update hosts file**
   Add to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
   ```
   127.0.0.1 branchloans.com
   ```

4. **Run development environment**
   ```bash
   docker-compose up -d --build
   docker-compose exec api alembic upgrade head
   docker-compose exec api python scripts/seed.py
   ```

5. **Access the application**
   - HTTPS: https://branchloans.com
   - API Direct: http://localhost:8000

## Environment Management

### Switching Environments

**Development** (default):
```bash
docker-compose up -d
```

**Staging**:
```bash
cp .env.staging .env
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

**Production**:
```bash
cp .env.prod .env
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Application environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:postgres@db:5432/microloans` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_NAME` | Database name | `microloans` |
| `PORT` | API port | `8000` |

## API Endpoints

### Health Check
- `GET /health` - Service health status
  ```bash
  curl https://branchloans.com/health
  ```

### Loan Management
- `GET /api/loans` - List all loans
  ```bash
  curl https://branchloans.com/api/loans
  ```

- `GET /api/loans/:id` - Get specific loan
  ```bash
  curl https://branchloans.com/api/loans/00000000-0000-0000-0000-000000000001
  ```

- `POST /api/loans` - Create new loan
  ```bash
  curl -X POST https://branchloans.com/api/loans \
    -H 'Content-Type: application/json' \
    -d '{
      "borrower_id": "usr_india_999",
      "amount": 12000.50,
      "currency": "INR",
      "term_months": 6,
      "interest_rate_apr": 24.0
    }'
  ```

### Statistics
- `GET /api/stats` - Loan statistics
  ```bash
  curl https://branchloans.com/api/stats
  ```

## CI/CD Pipeline

The GitHub Actions pipeline automates the entire build and deployment process:

### Pipeline Stages

1. **Test Stage**: Runs unit tests with PostgreSQL service
2. **Build Stage**: Builds Docker image with git SHA tags
3. **Security Scan**: Trivy vulnerability scanning for critical issues
4. **Push Stage**: Pushes secure images to GitHub Container Registry

### Pipeline Triggers
- **Push to `main` branch**: Full CI/CD pipeline (test → build → scan → push)
- **Pull requests**: Test stage only (no image pushing)

### Secrets Management
- Container registry credentials use `GITHUB_TOKEN`
- Database credentials stored as GitHub Secrets
- No sensitive data exposed in pipeline logs

## Project Structure

```
dummy-branch-app/
├── .github/workflows/
│   └── ci-cd.yml              # CI/CD pipeline
├── alembic/                   # Database migrations
├── app/                       # Flask application
│   ├── routes/               # API endpoints
│   ├── config.py             # Configuration
│   ├── db.py                 # Database setup
│   └── models.py             # Data models
├── nginx/
│   └── nginx.conf            # Nginx configuration
├── scripts/
│   ├── seed.py               # Database seeding
│   └── setup-local-ssl.sh    # SSL setup script
├── ssl/                      # SSL certificates
├── .env.dev                  # Development environment
├── .env.staging              # Staging environment
├── .env.prod                 # Production environment
├── docker-compose.yml        # Base compose file
├── docker-compose.staging.yml # Staging overrides
├── docker-compose.prod.yml   # Production overrides
└── Dockerfile               # Application container
```

## Design Decisions

### Containerization Strategy
- **Multi-container Docker setup** with Nginx reverse proxy
- **HTTPS termination** at Nginx level for security
- **Self-signed certificates** for local development
- **Health checks** for all services

### Multi-Environment Approach
- **Docker Compose overrides** for environment-specific configurations
- **Environment variables** for runtime configuration
- **Single Dockerfile** with multi-stage build capability
- **Resource limits** scaled by environment

### CI/CD Implementation
- **GitHub Actions** for native integration
- **Trivy security scanning** for vulnerability detection
- **Git SHA tagging** for precise version tracking
- **Fail-fast approach** with sequential stages

## Troubleshooting

### Common Issues

1. **SSL Certificate Warnings**
   - **Cause**: Self-signed certificates not trusted by browser
   - **Solution**: Accept the security exception in your browser

2. **Host Resolution Issues**
   - **Cause**: Missing hosts file entry
   - **Solution**: Verify `/etc/hosts` contains `127.0.0.1 branchloans.com`

3. **Database Connection Errors**
   - **Cause**: PostgreSQL not ready or credentials incorrect
   - **Solution**: Check container health: `docker-compose ps`

4. **Port Conflicts**
   - **Cause**: Other services using required ports
   - **Solution**: Stop conflicting services or modify ports in compose files

5. **Container Build Failures**
   - **Cause**: Docker cache issues or network problems
   - **Solution**: Rebuild with `--no-cache` flag: `docker-compose build --no-cache`

### Health Checks

```bash
# Check all services status
docker-compose ps

# Check API health endpoint
curl -k https://branchloans.com/health

# Check database connectivity
docker-compose exec db pg_isready -U postgres -d microloans

# View application logs
docker-compose logs api

# View nginx logs
docker-compose logs nginx

# View database logs
docker-compose logs db
```

### Debugging Steps

1. **Verify all containers are running**:
   ```bash
   docker-compose ps
   ```

2. **Check container logs for errors**:
   ```bash
   docker-compose logs
   ```

3. **Test database connection**:
   ```bash
   docker-compose exec db psql -U postgres -d microloans -c "SELECT version();"
   ```

4. **Verify SSL certificate**:
   ```bash
   openssl x509 -in ssl/branchloans.com.crt -text -noout
   ```

5. **Test API directly**:
   ```bash
   curl http://localhost:8000/health
   ```

## Development

### Adding New Features

1. **Database Changes**:
   - Create new migration: `alembic revision -m "description"`
   - Implement upgrade/downgrade in migration file
   - Run migration: `alembic upgrade head`

2. **API Endpoints**:
   - Add new route in `app/routes/`
   - Register blueprint in `app/__init__.py`
   - Update models/schemas as needed

3. **Environment Variables**:
   - Add to `app/config.py`
   - Update all `.env.*` files
   - Document in README

### Testing

Run the test suite:
```bash
# Using local Python
pytest test_app.py -v

# Using Docker
docker-compose exec api pytest test_app.py -v
```

## Security Considerations

- **HTTPS enforced** in all environments
- **Security scanning** in CI pipeline
- **No hardcoded secrets** - all via environment variables
- **Database password** configurable per environment
- **Resource limits** to prevent DoS attacks

## Performance

### Resource Allocation
- **Development**: Minimal resources for local development
- **Staging**: Moderate resources mimicking production
- **Production**: Optimized resources with persistence

### Optimization Tips
- Use `--build` flag only when dependencies change
- Leverage Docker layer caching for faster builds
- Monitor resource usage: `docker stats`
- Scale workers in production: modify `-w` parameter in gunicorn

## Future Improvements

With more time, the following enhancements would be valuable:

1. **Observability**
   - Prometheus metrics endpoint
   - Grafana dashboards for monitoring
   - Structured JSON logging
   - Request tracing with correlation IDs

2. **Database Optimization**
   - Connection pooling with PGBouncer
   - Read replicas for scaling
   - Database backup strategies
   - Connection health monitoring

3. **Security Enhancements**
   - JWT authentication
   - Rate limiting
   - Web Application Firewall (WAF)
   - Secret rotation automation

4. **Infrastructure as Code**
   - Terraform for cloud deployment
   - Kubernetes manifests
   - Service mesh integration
   - Blue-green deployment strategies

5. **Monitoring & Alerting**
   - ELK stack for log aggregation
   - AlertManager for notifications
   - Performance benchmarking
   - Capacity planning

6. **Developer Experience**
   - Makefile for common tasks
   - Local development with telepresence
   - Automated database seeding
   - Integration test suite

## Support

For issues and questions:
1. Check this README and troubleshooting section
2. Review Docker and container logs
3. Verify environment configuration
4. Ensure all prerequisites are met

## License

This project is part of the Branch DevOps Intern Take-Home Assignment.
