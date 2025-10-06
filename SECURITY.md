# Security Best Practices for MarketingIQ

## Overview
This document outlines security measures implemented and recommended practices for the MarketingIQ system.

## Current Security Implementation

### 1. Password Management
- **Strong Password Generation**: Automated generation of 32-character passwords
- **Secret Storage**: Passwords stored in `secrets/` directory with restricted permissions
- **Never in Code**: Passwords never hardcoded in source files
- **Docker Secrets**: Production deployment uses Docker secrets

### 2. Database Security
- **Encrypted Connections**: TrustServerCertificate for development, proper SSL for production
- **Connection Pooling**: Limited concurrent connections
- **Parameterized Queries**: Protection against SQL injection
- **Least Privilege**: Consider creating specific users instead of using `sa`

### 3. API Security
- **CORS Configuration**: Properly configured cross-origin policies
- **Rate Limiting**: Should be implemented (see recommendations)
- **Authentication**: Should be added (see recommendations)
- **Input Validation**: Pydantic models validate all inputs

### 4. Configuration Security
- **Encrypted Config**: Sensitive data encrypted using Fernet encryption
- **Environment Variables**: Used for configuration, not hardcoded
- **Gitignore**: All sensitive files excluded from version control

### 5. Backup Security
- **Encrypted Backups**: Backups compressed and can be encrypted
- **Retention Policy**: Automatic cleanup of old backups
- **Secure Storage**: Backups stored with restricted permissions

## Production Deployment Checklist

### Before Deployment:
- [ ] Generate new strong passwords using `python secure_config.py`
- [ ] Change default SA password
- [ ] Create application-specific database users
- [ ] Enable SQL Server SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up VPN or private network
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Set up monitoring alerts
- [ ] Implement API authentication
- [ ] Add rate limiting
- [ ] Enable HTTPS for API
- [ ] Review and restrict CORS origins
- [ ] Set up intrusion detection
- [ ] Configure log aggregation

### Secrets Management:
```bash
# Generate secure passwords
python secure_config.py

# Store in Docker secrets (production)
echo "YourSecurePassword" | docker secret create db_password -
echo "YourGrafanaPassword" | docker secret create grafana_password -
```

### File Permissions:
```bash
# Restrict sensitive file permissions
chmod 600 .env
chmod 600 .key
chmod 600 secrets/*
chmod 600 config.encrypted
chmod 700 secrets/
```

## Recommended Improvements

### 1. Authentication & Authorization
```python
# Add JWT authentication to API
from fastapi_jwt_auth import AuthJWT

@app.post('/login')
async def login(credentials: UserCredentials, Authorize: AuthJWT = Depends()):
    # Verify credentials
    access_token = Authorize.create_access_token(subject=user.id)
    return {"access_token": access_token}

@app.get('/protected')
async def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"user": Authorize.get_jwt_subject()}
```

### 2. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get('/api/campaigns')
@limiter.limit("100/minute")
async def get_campaigns(request: Request):
    # Your code here
```

### 3. Database User Separation
```sql
-- Create application user with limited permissions
CREATE LOGIN app_user WITH PASSWORD = 'StrongAppPassword123!';
CREATE USER app_user FOR LOGIN app_user;

-- Grant only necessary permissions
GRANT SELECT, INSERT, UPDATE ON SCHEMA::dw TO app_user;
DENY DELETE ON SCHEMA::dw TO app_user;

-- Create read-only user for reporting
CREATE LOGIN report_user WITH PASSWORD = 'StrongReportPassword123!';
CREATE USER report_user FOR LOGIN report_user;
GRANT SELECT ON SCHEMA::dw TO report_user;
```

### 4. SSL/TLS Configuration
```yaml
# docker-compose-prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - api
```

### 5. Audit Logging
```python
from loguru import logger

# Configure audit logging
logger.add(
    "audit.log",
    rotation="1 day",
    retention="90 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    filter=lambda record: "audit" in record["extra"]
)

# Log security events
logger.bind(audit=True).info(f"User {user_id} accessed {endpoint}")
```

## Security Monitoring

### Key Metrics to Monitor:
- Failed login attempts
- Unusual query patterns
- Large data exports
- Connection spikes
- Error rate increases
- Response time anomalies

### Alert Thresholds:
- CPU > 80% for 5 minutes
- Memory > 90%
- Failed logins > 5 in 1 minute
- Database connections > 90% of pool
- API errors > 10% of requests
- Disk usage > 85%

## Incident Response Plan

### If Breach Suspected:
1. **Immediate Actions**:
   - Rotate all passwords
   - Review access logs
   - Check for unauthorized changes
   - Isolate affected systems

2. **Investigation**:
   - Analyze audit logs
   - Check for data exfiltration
   - Identify attack vector
   - Document timeline

3. **Recovery**:
   - Restore from clean backup
   - Apply security patches
   - Update security rules
   - Notify stakeholders

## Compliance Considerations

### GDPR Compliance:
- Implement data retention policies
- Add data anonymization features
- Provide data export capabilities
- Log all data access

### Security Headers:
```python
from fastapi.middleware.security import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    x_content_type_options="nosniff",
    x_frame_options="DENY",
    x_xss_protection="1; mode=block",
    strict_transport_security="max-age=31536000; includeSubDomains"
)
```

## Regular Security Tasks

### Daily:
- Review error logs
- Check backup completion
- Monitor system resources

### Weekly:
- Review access logs
- Check for security updates
- Test backup restoration

### Monthly:
- Rotate passwords
- Review user permissions
- Security vulnerability scan
- Update dependencies

### Quarterly:
- Security audit
- Penetration testing
- Disaster recovery drill
- Policy review

## Contact Information

For security concerns or incidents:
- Security Team: [your-security-email]
- Emergency: [your-emergency-contact]

## Version History
- v1.0 - Initial security implementation
- v2.0 - Added SQL Server security features