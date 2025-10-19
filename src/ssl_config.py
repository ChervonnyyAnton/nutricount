"""
SSL/HTTPS Configuration Module
Handles SSL certificates and HTTPS configuration
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
from flask import request, redirect, jsonify

logger = logging.getLogger(__name__)

class SSLManager:
    """Manages SSL certificates and HTTPS configuration"""
    
    def __init__(self, cert_dir: str = "ssl"):
        self.cert_dir = Path(cert_dir)
        self.cert_file = self.cert_dir / "cert.pem"
        self.key_file = self.cert_dir / "key.pem"
        self.ca_file = self.cert_dir / "ca.pem"
        
        # Create SSL directory if it doesn't exist
        self.cert_dir.mkdir(exist_ok=True)
    
    def generate_self_signed_cert(self, hostname: str = "localhost", 
                                 country: str = "US", state: str = "State", 
                                 city: str = "City", org: str = "Organization") -> bool:
        """Generate self-signed SSL certificate"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta, timezone
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
                x509.NameAttribute(NameOID.LOCALITY_NAME, city),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
                x509.NameAttribute(NameOID.COMMON_NAME, hostname),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(hostname),
                    x509.DNSName("localhost"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write private key
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            logger.info(f"Self-signed certificate generated for {hostname}")
            return True
            
        except ImportError:
            logger.error("cryptography library not available for SSL certificate generation")
            return False
        except Exception as e:
            logger.error(f"SSL certificate generation error: {e}")
            return False
    
    def get_certificate_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current certificate"""
        try:
            if not self.cert_file.exists():
                return None
            
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            
            with open(self.cert_file, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            return {
                'subject': dict(cert.subject),
                'issuer': dict(cert.issuer),
                'serial_number': str(cert.serial_number),
                'not_valid_before': cert.not_valid_before.isoformat(),
                'not_valid_after': cert.not_valid_after.isoformat(),
                'version': cert.version.name,
                'signature_algorithm': cert.signature_algorithm_oid._name,
            }
            
        except Exception as e:
            logger.error(f"Certificate info error: {e}")
            return None
    
    def is_certificate_valid(self) -> bool:
        """Check if certificate is valid and not expired"""
        try:
            if not self.cert_file.exists() or not self.key_file.exists():
                return False
            
            from cryptography import x509
            from datetime import datetime, timezone
            
            with open(self.cert_file, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            now = datetime.now(timezone.utc)
            return cert.not_valid_before <= now <= cert.not_valid_after
            
        except Exception as e:
            logger.error(f"Certificate validation error: {e}")
            return False
    
    def get_ssl_context(self):
        """Get SSL context for Flask/Gunicorn"""
        try:
            import ssl
            
            if not self.is_certificate_valid():
                logger.warning("SSL certificate is not valid")
                return None
            
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(str(self.cert_file), str(self.key_file))
            
            # Security settings
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            
            return context
            
        except Exception as e:
            logger.error(f"SSL context creation error: {e}")
            return None

class HTTPSRedirect:
    """Handles HTTPS redirects"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.before_request(self.force_https)
    
    def force_https(self):
        """Force HTTPS redirect"""
        if not request.is_secure:
            # Skip for health checks and metrics
            if request.endpoint in ['health', 'prometheus_metrics']:
                return
            
            # Skip for localhost in development
            if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
                return
            
            # Redirect to HTTPS
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

class SecurityConfig:
    """Security configuration settings"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = False
    
    # Token settings
    ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRY = 2592000  # 30 days
    
    # Rate limiting
    RATE_LIMITS = {
        'api': {'requests': 100, 'window': 3600},
        'auth': {'requests': 10, 'window': 3600},
        'admin': {'requests': 200, 'window': 3600},
    }
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
    
    # CORS settings
    CORS_ORIGINS = ['https://localhost', 'https://127.0.0.1']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # Session settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

def setup_security_middleware(app):
    """Setup security middleware for Flask app"""
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    # Add CORS headers
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in SecurityConfig.CORS_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(SecurityConfig.CORS_METHODS)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(SecurityConfig.CORS_HEADERS)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Add request logging
    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    # Add error handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        return jsonify({'error': 'Rate limit exceeded', 'message': 'Too many requests'}), 429

# Global SSL manager instance
ssl_manager = SSLManager()
