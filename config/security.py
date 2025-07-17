"""
Sistema Mayra - Security Configuration
Security configurations, constants, and utility functions.
"""

import os
import secrets
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    import jwt
    from passlib.context import CryptContext
    from cryptography.fernet import Fernet
    HAS_CRYPTO_LIBS = True
except ImportError:
    HAS_CRYPTO_LIBS = False


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionLevel(Enum):
    """Permission levels for users."""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_access_token_expire_minutes: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    jwt_refresh_token_expire_days: int = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    # Password Configuration
    password_min_length: int = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    password_max_length: int = int(os.getenv('PASSWORD_MAX_LENGTH', '128'))
    password_require_uppercase: bool = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    password_require_lowercase: bool = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    password_require_numbers: bool = os.getenv('PASSWORD_REQUIRE_NUMBERS', 'True').lower() == 'true'
    password_require_symbols: bool = os.getenv('PASSWORD_REQUIRE_SYMBOLS', 'True').lower() == 'true'
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '60'))
    rate_limit_requests_per_hour: int = int(os.getenv('RATE_LIMIT_REQUESTS_PER_HOUR', '1000'))
    rate_limit_requests_per_day: int = int(os.getenv('RATE_LIMIT_REQUESTS_PER_DAY', '10000'))
    
    # Session Configuration
    session_timeout_minutes: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    session_max_concurrent: int = int(os.getenv('SESSION_MAX_CONCURRENT', '3'))
    
    # API Security
    api_key_length: int = int(os.getenv('API_KEY_LENGTH', '32'))
    api_key_prefix: str = os.getenv('API_KEY_PREFIX', 'sk_mayra_')
    
    # Encryption
    encryption_key: str = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode() if HAS_CRYPTO_LIBS else '')
    
    # Telegram Security
    telegram_webhook_secret: str = os.getenv('TELEGRAM_WEBHOOK_SECRET', secrets.token_urlsafe(32))
    telegram_max_message_length: int = int(os.getenv('TELEGRAM_MAX_MESSAGE_LENGTH', '4096'))
    
    # CORS Configuration
    cors_allowed_origins: List[str] = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
    cors_allowed_methods: List[str] = os.getenv('CORS_ALLOWED_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
    cors_allowed_headers: List[str] = os.getenv('CORS_ALLOWED_HEADERS', 'Content-Type,Authorization').split(',')
    cors_max_age: int = int(os.getenv('CORS_MAX_AGE', '86400'))
    
    # Security Headers
    security_headers: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize security headers."""
        if self.security_headers is None:
            self.security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
            }


class SecurityManager:
    """Main security manager class."""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        
        if HAS_CRYPTO_LIBS:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            self.fernet = Fernet(self.config.encryption_key.encode()) if self.config.encryption_key else None
        else:
            self.pwd_context = None
            self.fernet = None
    
    # Password Management
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not self.pwd_context:
            raise RuntimeError("Password hashing requires passlib library")
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not self.pwd_context:
            raise RuntimeError("Password verification requires passlib library")
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to security policy."""
        result = {
            'valid': True,
            'errors': [],
            'score': 0
        }
        
        # Length check
        if len(password) < self.config.password_min_length:
            result['valid'] = False
            result['errors'].append(f"Password must be at least {self.config.password_min_length} characters long")
        elif len(password) > self.config.password_max_length:
            result['valid'] = False
            result['errors'].append(f"Password must be no more than {self.config.password_max_length} characters long")
        else:
            result['score'] += 1
        
        # Character requirements
        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one uppercase letter")
        else:
            result['score'] += 1
        
        if self.config.password_require_lowercase and not any(c.islower() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one lowercase letter")
        else:
            result['score'] += 1
        
        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one number")
        else:
            result['score'] += 1
        
        if self.config.password_require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one special character")
        else:
            result['score'] += 1
        
        # Common password check
        if password.lower() in ['password', '123456', 'qwerty', 'abc123', 'password123']:
            result['valid'] = False
            result['errors'].append("Password is too common")
        else:
            result['score'] += 1
        
        return result
    
    # JWT Token Management
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if not HAS_CRYPTO_LIBS:
            raise RuntimeError("JWT token creation requires PyJWT library")
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.jwt_access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        if not HAS_CRYPTO_LIBS:
            raise RuntimeError("JWT token creation requires PyJWT library")
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.jwt_refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        if not HAS_CRYPTO_LIBS:
            raise RuntimeError("JWT token verification requires PyJWT library")
        
        try:
            payload = jwt.decode(token, self.config.jwt_secret_key, algorithms=[self.config.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    # API Key Management
    def generate_api_key(self, user_id: str) -> str:
        """Generate a secure API key."""
        random_part = secrets.token_urlsafe(self.config.api_key_length)
        api_key = f"{self.config.api_key_prefix}{random_part}"
        return api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format."""
        if not api_key.startswith(self.config.api_key_prefix):
            return False
        
        key_part = api_key[len(self.config.api_key_prefix):]
        if len(key_part) != self.config.api_key_length:
            return False
        
        # Check if it's a valid base64 URL-safe string
        try:
            base64.urlsafe_b64decode(key_part + '==')
            return True
        except:
            return False
    
    # Data Encryption
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.fernet:
            raise RuntimeError("Data encryption requires cryptography library and encryption key")
        
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.fernet:
            raise RuntimeError("Data decryption requires cryptography library and encryption key")
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    # HMAC Verification
    def create_hmac_signature(self, message: str, secret: str) -> str:
        """Create HMAC signature for message verification."""
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_hmac_signature(self, message: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self.create_hmac_signature(message, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    # Telegram Webhook Security
    def verify_telegram_webhook(self, body: str, signature: str) -> bool:
        """Verify Telegram webhook signature."""
        return self.verify_hmac_signature(body, signature, self.config.telegram_webhook_secret)
    
    # Session Management
    def create_session_token(self, user_id: str, additional_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a session token."""
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=self.config.session_timeout_minutes)).isoformat()
        }
        
        if additional_data:
            session_data.update(additional_data)
        
        return self.create_access_token(session_data)
    
    def validate_session_token(self, token: str) -> Dict[str, Any]:
        """Validate session token."""
        try:
            payload = self.verify_token(token)
            
            # Check if session has expired
            expires_at = datetime.fromisoformat(payload.get('expires_at', ''))
            if datetime.utcnow() > expires_at:
                raise ValueError("Session has expired")
            
            return payload
        except Exception as e:
            raise ValueError(f"Invalid session token: {str(e)}")
    
    # Input Sanitization
    def sanitize_input(self, input_data: str, max_length: int = 1000) -> str:
        """Sanitize user input."""
        if not input_data:
            return ""
        
        # Trim whitespace
        sanitized = input_data.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        import re
        # Simple international phone number validation
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.requests = {}  # In production, use Redis or similar
    
    def is_allowed(self, identifier: str, limit_type: str = "minute") -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.utcnow()
        
        # Get limit based on type
        if limit_type == "minute":
            limit = self.config.rate_limit_requests_per_minute
            window = timedelta(minutes=1)
        elif limit_type == "hour":
            limit = self.config.rate_limit_requests_per_hour
            window = timedelta(hours=1)
        elif limit_type == "day":
            limit = self.config.rate_limit_requests_per_day
            window = timedelta(days=1)
        else:
            return False
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < window
            ]
        else:
            self.requests[identifier] = []
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= limit:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str, limit_type: str = "minute") -> int:
        """Get remaining requests for identifier."""
        now = datetime.utcnow()
        
        if limit_type == "minute":
            limit = self.config.rate_limit_requests_per_minute
            window = timedelta(minutes=1)
        elif limit_type == "hour":
            limit = self.config.rate_limit_requests_per_hour
            window = timedelta(hours=1)
        elif limit_type == "day":
            limit = self.config.rate_limit_requests_per_day
            window = timedelta(days=1)
        else:
            return 0
        
        if identifier not in self.requests:
            return limit
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < window
        ]
        
        return max(0, limit - len(self.requests[identifier]))


class SecurityAuditLogger:
    """Security audit logging."""
    
    def __init__(self, logger=None):
        self.logger = logger or self._get_default_logger()
    
    def _get_default_logger(self):
        """Get default logger for security events."""
        import logging
        logger = logging.getLogger('security')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def log_authentication_success(self, user_id: str, ip_address: str, **context):
        """Log successful authentication."""
        self.logger.info(f"Authentication successful for user {user_id} from {ip_address}", extra={
            'event_type': 'authentication_success',
            'user_id': user_id,
            'ip_address': ip_address,
            **context
        })
    
    def log_authentication_failure(self, user_id: str, ip_address: str, reason: str, **context):
        """Log failed authentication."""
        self.logger.warning(f"Authentication failed for user {user_id} from {ip_address}: {reason}", extra={
            'event_type': 'authentication_failure',
            'user_id': user_id,
            'ip_address': ip_address,
            'reason': reason,
            **context
        })
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str, **context):
        """Log authorization failure."""
        self.logger.warning(f"Authorization failed for user {user_id} accessing {resource} with action {action}", extra={
            'event_type': 'authorization_failure',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            **context
        })
    
    def log_rate_limit_exceeded(self, identifier: str, limit_type: str, **context):
        """Log rate limit exceeded."""
        self.logger.warning(f"Rate limit exceeded for {identifier} ({limit_type})", extra={
            'event_type': 'rate_limit_exceeded',
            'identifier': identifier,
            'limit_type': limit_type,
            **context
        })
    
    def log_suspicious_activity(self, user_id: str, activity: str, **context):
        """Log suspicious activity."""
        self.logger.error(f"Suspicious activity detected for user {user_id}: {activity}", extra={
            'event_type': 'suspicious_activity',
            'user_id': user_id,
            'activity': activity,
            **context
        })


# Global security manager instance
security_manager = SecurityManager()
rate_limiter = RateLimiter()
security_audit_logger = SecurityAuditLogger()


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    return security_manager


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return rate_limiter


def get_security_audit_logger() -> SecurityAuditLogger:
    """Get the global security audit logger instance."""
    return security_audit_logger


def initialize_security(config: SecurityConfig = None):
    """Initialize security components with configuration."""
    global security_manager, rate_limiter, security_audit_logger
    
    config = config or SecurityConfig()
    security_manager = SecurityManager(config)
    rate_limiter = RateLimiter(config)
    security_audit_logger = SecurityAuditLogger()
    
    return security_manager, rate_limiter, security_audit_logger