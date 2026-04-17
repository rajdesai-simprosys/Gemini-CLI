# Gemini-CLI

A FastAPI application demonstrating advanced patterns.

## Features
- **Sliding Window Rate Limiting**: Advanced decorator to protect endpoints.

## Rate Limiting Usage

The project includes a custom asynchronous rate limiter located in `rate_limiter.py`.

### Implementation
The `rate_limit` decorator uses a sliding window algorithm to track requests per client IP.

### Example Usage

To use the rate limiter, ensure your FastAPI endpoint accepts a `Request` object:

```python
from fastapi import Request
from rate_limiter import rate_limit

@app.get("/secure-data")
@rate_limit(times=5, seconds=60)
async def get_secure_data(request: Request):
    return {"data": "This is protected by rate limiting"}
```

#### Parameters:
- `times`: Number of allowed requests within the window.
- `seconds`: The duration of the sliding window in seconds.

### Error Handling
When the limit is exceeded, the API returns a `429 Too Many Requests` status code with a `Retry-After` header.
