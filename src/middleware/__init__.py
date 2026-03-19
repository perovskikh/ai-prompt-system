# src/middleware/__init__.py
"""
Middleware package for AI Prompt System.

Provides:
- Baseline verification middleware
- JWT authentication service
- Tier-based RBAC (Role-Based Access Control)
- Cascade priority logic middleware
"""

from .baseline_verification import (
    BaselineVerificationError,
    BaselineVerificationConfig,
    verify_baseline_on_startup,
    baseline_verification_middleware,
    verify_baseline_decorator,
    configure_baseline_verification,
    verification_config
)

from .jwt_auth import (
    JWTService,
    TokenPayload,
    get_jwt_service,
    DEFAULT_ROLES,
    require_auth
)

from .rbac import (
    RBACService,
    Role,
    Tier,
    Permission,
    AccessContext,
    get_rbac_service,
    ROLE_PERMISSIONS,
    ROLE_TIER_ACCESS
)

__all__ = [
    # Baseline verification
    "BaselineVerificationError",
    "BaselineVerificationConfig",
    "verify_baseline_on_startup",
    "baseline_verification_middleware",
    "verify_baseline_decorator",
    "configure_baseline_verification",
    "verification_config",
    # JWT Auth
    "JWTService",
    "TokenPayload",
    "get_jwt_service",
    "DEFAULT_ROLES",
    "require_auth",
    # RBAC
    "RBACService",
    "Role",
    "Tier",
    "Permission",
    "AccessContext",
    "get_rbac_service",
    "ROLE_PERMISSIONS",
    "ROLE_TIER_ACCESS"
]
