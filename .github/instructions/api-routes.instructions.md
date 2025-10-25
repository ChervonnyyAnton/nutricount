# API Routes Development Instructions

**Applies to**: `**/routes/**/*.py`, `**/api/**/*.py`, `app.py` routes

## API Development Requirements

### Always Validate All Inputs

```python
from src.utils import validate_input, json_response

@products_bp.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error = validate_input(data, ['name', 'calories'])
    if not is_valid:
        return json_response({"error": error}, 400)
    
    # Validate data types and ranges
    try:
        calories = int(data['calories'])
        if calories < 0:
            return json_response({"error": "Calories must be positive"}, 400)
    except (ValueError, TypeError):
        return json_response({"error": "Invalid calories value"}, 400)
    
    # Process valid data
    product_id = create_product_in_db(data)
    return json_response({"id": product_id, "success": True}, 200)
```

### Use Appropriate HTTP Status Codes

- **200 OK**: Successful GET, PUT, DELETE
- **201 Created**: Successful POST (resource created)
- **400 Bad Request**: Invalid input, validation errors
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource already exists, duplicate error
- **422 Unprocessable Entity**: Valid syntax but semantic error
- **500 Internal Server Error**: Unexpected server errors

```python
# Examples
return json_response({"data": result}, 200)  # Success
return json_response({"error": "Invalid input"}, 400)  # Validation error
return json_response({"error": "Unauthorized"}, 401)  # Auth required
return json_response({"error": "Not found"}, 404)  # Resource missing
return json_response({"error": "Internal error"}, 500)  # Server error
```

### Implement Comprehensive Error Handling

```python
from src.advanced_logging import structured_logger as logger

@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a product by ID"""
    try:
        product = fetch_product(product_id)
        
        if not product:
            return json_response({"error": "Product not found"}, 404)
        
        return json_response({"data": product}, 200)
        
    except ValueError as e:
        logger.warning(f"Invalid product ID: {product_id}", exc_info=True)
        return json_response({"error": "Invalid product ID"}, 400)
        
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        return json_response({"error": "Failed to fetch product"}, 500)
```

### Document Every Endpoint

```python
@products_bp.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product.
    
    Request Body:
        {
            "name": str (required) - Product name
            "calories": int (required) - Calories per 100g
            "protein": float (optional) - Protein in grams
            "carbs": float (optional) - Carbohydrates in grams
            "fat": float (optional) - Fat in grams
            "fiber": float (optional) - Fiber in grams
        }
    
    Returns:
        200: {"id": int, "success": true}
        400: {"error": str}
        500: {"error": str}
    
    Example:
        POST /api/products
        {
            "name": "Apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2,
            "fiber": 2.4
        }
        
        Response: {"id": 123, "success": true}
    """
    pass
```

### Rate Limiting for Public Endpoints

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")  # Stricter limit for auth
def login():
    """User login with rate limiting"""
    pass

@products_bp.route('/api/products', methods=['GET'])
@limiter.limit("200 per hour")  # Higher limit for reads
def list_products():
    """List products with rate limiting"""
    pass
```

### Log All Requests and Responses

```python
from src.advanced_logging import structured_logger as logger

@app.before_request
def log_request():
    """Log incoming request"""
    logger.info(
        "Incoming request",
        method=request.method,
        path=request.path,
        ip=request.remote_addr,
        user_agent=request.user_agent.string
    )

@app.after_request
def log_response(response):
    """Log outgoing response"""
    logger.info(
        "Outgoing response",
        method=request.method,
        path=request.path,
        status=response.status_code,
        size=response.content_length
    )
    return response
```

### Security Requirements

**Helmet-style security headers**:

```python
from src.security import SecurityHeaders

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    return SecurityHeaders.add_security_headers(response)
```

**CORS configuration**:

```python
from flask_cors import CORS

# Configure CORS for API endpoints only
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**Input sanitization**:

```python
import html
from werkzeug.utils import secure_filename

def sanitize_input(data):
    """Sanitize user input to prevent XSS"""
    if isinstance(data, str):
        return html.escape(data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

@products_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    data = sanitize_input(data)  # Sanitize all inputs
    # Process sanitized data
```

**Parameterized queries** (prevent SQL injection):

```python
# Good - Parameterized query
cursor.execute(
    "SELECT * FROM products WHERE id = ?",
    (product_id,)
)

# Bad - SQL injection vulnerable
cursor.execute(f"SELECT * FROM products WHERE id = {product_id}")
```

### Never Expose Stack Traces to Users

```python
# Bad - Exposes internals
@products_bp.route('/api/products', methods=['POST'])
def create_product():
    try:
        result = operation()
    except Exception as e:
        return json_response({"error": str(e)}, 500)  # DON'T DO THIS

# Good - User-friendly error
@products_bp.route('/api/products', methods=['POST'])
def create_product():
    try:
        result = operation()
    except ValueError:
        return json_response({"error": "Invalid input data"}, 400)
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        return json_response({"error": "Failed to create product"}, 500)
```

### Response Format Consistency

```python
# Success response
{
    "success": true,
    "data": {...} or [...],
    "meta": {  # Optional metadata
        "page": 1,
        "total": 100,
        "per_page": 20
    }
}

# Error response
{
    "error": "Error message",
    "details": {...},  # Optional details for debugging (dev only)
    "code": "ERROR_CODE"  # Optional error code
}

# Example implementations
def success_response(data, meta=None):
    response = {"success": True, "data": data}
    if meta:
        response["meta"] = meta
    return json_response(response, 200)

def error_response(message, code=None, status=400):
    response = {"error": message}
    if code:
        response["code"] = code
    return json_response(response, status)
```

### Authentication Middleware

```python
from functools import wraps
from src.security import verify_jwt_token

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return json_response({"error": "Unauthorized"}, 401)
        
        is_valid, payload = verify_jwt_token(token)
        if not is_valid:
            return json_response({"error": "Invalid or expired token"}, 401)
        
        # Attach user info to request
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        
        return f(*args, **kwargs)
    
    return decorated_function

@products_bp.route('/api/products', methods=['POST'])
@require_auth
def create_product():
    """Create product (authentication required)"""
    user_id = request.user_id  # Available via decorator
    pass
```

## Quick Checklist

- [ ] All inputs validated
- [ ] Appropriate HTTP status codes
- [ ] Comprehensive error handling
- [ ] Endpoint documented with examples
- [ ] Rate limiting applied
- [ ] Request/response logged
- [ ] Security headers added
- [ ] Input sanitized
- [ ] Parameterized queries used
- [ ] No stack traces exposed
- [ ] Consistent response format
- [ ] Authentication/authorization implemented
- [ ] Tests written (unit + integration)
- [ ] Tested with curl/Postman
