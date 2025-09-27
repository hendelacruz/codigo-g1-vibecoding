# Rate Limiting System Documentation

## Overview

This document describes the comprehensive rate limiting system implemented in the Django API to protect against abuse and ensure fair usage of resources.

## Architecture

### Components

1. **RateLimitMiddleware**: Global middleware for basic rate limiting
2. **APIRateLimitMixin**: Mixin for ViewSet-specific rate limiting
3. **@rate_limit decorator**: Method-specific rate limiting
4. **Redis Cache Backend**: Storage for rate limit counters
5. **Logging System**: Monitoring and alerting for rate limit violations

### Rate Limiting Strategies

#### 1. Sliding Window Algorithm
- Uses Redis to store request counts with timestamps
- Provides smooth rate limiting without burst allowances
- Automatically expires old data

#### 2. Multiple Time Windows
- Per-minute limits for burst protection
- Per-hour limits for sustained usage
- Both limits must be respected

## Configuration

### Global Settings (`settings/base.py`)

```python
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 3600},  # 100/hour
    'auth': {'requests': 20, 'window': 3600},      # 20/hour for auth
    'strict': {'requests': 10, 'window': 3600},    # 10/hour for sensitive ops
}
```

### ViewSet Configuration

```python
class VentasViewSet(APIRateLimitMixin, BusinessIntelligenceViewSet):
    rate_limit_scope = 'sales'
    rate_limit_config = {'requests': 200, 'window': 3600}
```

### Method-Specific Limits

```python
@rate_limit(requests_per_hour=50, requests_per_minute=5)
def create(self, request):
    # Limited creation endpoint
    pass
```

## Rate Limits by Endpoint

### Authentication Endpoints
- **Login**: 20 requests/hour, 3 requests/minute
- **Password Change**: 10 requests/hour, 2 requests/minute
- **Registration**: 5 requests/hour, 1 request/minute

### Sales Endpoints
- **General Operations**: 200 requests/hour
- **Create Sales**: 50 requests/hour, 5 requests/minute
- **Reports**: 20 requests/hour, 3 requests/minute

### Export Endpoints
- **Data Export**: 10 requests/hour, 2 requests/minute

### Default Limits
- **All Other Endpoints**: 100 requests/hour

## Client Identification

Rate limits are applied per client using the following hierarchy:

1. **Authenticated Users**: `user:{user_id}`
2. **API Key Users**: `api_key:{key_hash}`
3. **Anonymous Users**: `ip:{ip_address}`

## Response Format

### Successful Request
Normal API response with additional headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limited Request
```json
{
    "error": "Rate limit exceeded",
    "detail": "Maximum 100 requests per 3600 seconds allowed",
    "retry_after": 2847
}
```

HTTP Status: `429 Too Many Requests`

## Monitoring and Logging

### Log Files
- **General Logs**: `logs/django.log`
- **Rate Limit Logs**: `logs/rate_limits.log`

### Log Format
```
[RATE_LIMIT] 2024-01-15 10:30:45 WARNING Rate limit exceeded for client user:123 - IP: 192.168.1.100 - User: john_doe - Endpoint: /api/sales/
```

### Monitoring Command
```bash
python manage.py monitor_rate_limits --continuous --interval 60
```

## Implementation Details

### Middleware Flow
1. Extract client identifier from request
2. Determine rate limit configuration
3. Check current usage against limits
4. Update counters if within limits
5. Return 429 if limits exceeded
6. Log violations for monitoring

### Cache Keys
- Format: `rate_limit:{scope}:{client_id}:{window_type}`
- Example: `rate_limit:sales:user:123:hour`
- TTL: Automatically set to window duration

### Performance Considerations
- Redis operations are atomic
- Minimal overhead per request (~1-2ms)
- Automatic cleanup of expired keys
- Efficient sliding window implementation

## Security Features

### Protection Against
- **Brute Force Attacks**: Strict limits on authentication
- **API Abuse**: Per-endpoint rate limiting
- **Resource Exhaustion**: Export and report limits
- **Automated Scraping**: IP-based limits for anonymous users

### Bypass Prevention
- Multiple identification methods
- Consistent enforcement across all endpoints
- Logging for audit trails
- No easy bypass mechanisms

## Troubleshooting

### Common Issues

#### 1. Rate Limit False Positives
**Symptoms**: Legitimate users getting 429 errors
**Solutions**:
- Check if multiple users share same IP (NAT)
- Verify rate limit configurations
- Review user authentication status

#### 2. Redis Connection Issues
**Symptoms**: Rate limiting not working
**Solutions**:
- Verify Redis server status
- Check Django cache configuration
- Review Redis connection settings

#### 3. Performance Impact
**Symptoms**: Slow API responses
**Solutions**:
- Monitor Redis performance
- Check rate limiting overhead
- Optimize cache key patterns

### Debugging Commands

```bash
# Monitor current rate limits
python manage.py monitor_rate_limits

# Check Redis cache status
python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('rate_limit:default:user:123:hour')

# Clear rate limits for testing
python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete_pattern('rate_limit:*')
```

## Best Practices

### For Developers
1. Always test rate limits in development
2. Use appropriate limits for each endpoint type
3. Implement graceful degradation for rate-limited clients
4. Monitor rate limit logs regularly

### For API Consumers
1. Implement exponential backoff for 429 responses
2. Cache responses when possible
3. Use authentication to get higher limits
4. Monitor rate limit headers

### For Operations
1. Set up alerts for high rate limit violations
2. Monitor Redis performance and memory usage
3. Regularly review and adjust rate limits
4. Implement rate limit dashboards

## Future Enhancements

### Planned Features
1. **Dynamic Rate Limits**: Adjust based on server load
2. **User-Specific Limits**: Custom limits per user tier
3. **Geographic Limits**: Different limits by region
4. **Rate Limit Analytics**: Detailed usage statistics
5. **Whitelist/Blacklist**: IP-based allow/deny lists

### Integration Opportunities
1. **Prometheus Metrics**: Export rate limit metrics
2. **Grafana Dashboards**: Visual monitoring
3. **Slack Alerts**: Real-time notifications
4. **API Gateway**: Centralized rate limiting

## Configuration Examples

### Development Environment
```python
RATE_LIMITS = {
    'default': {'requests': 1000, 'window': 3600},  # Relaxed for testing
    'auth': {'requests': 100, 'window': 3600},
}
```

### Production Environment
```python
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 3600},   # Strict for production
    'auth': {'requests': 20, 'window': 3600},
    'strict': {'requests': 5, 'window': 3600},
}
```

### High-Traffic Environment
```python
RATE_LIMITS = {
    'default': {'requests': 500, 'window': 3600},   # Higher limits
    'auth': {'requests': 50, 'window': 3600},
    'premium': {'requests': 1000, 'window': 3600},  # Premium users
}
```

## Conclusion

The rate limiting system provides comprehensive protection against API abuse while maintaining good performance and user experience. Regular monitoring and adjustment of limits ensures optimal balance between security and usability.

For questions or issues, refer to the troubleshooting section or contact the development team.