# src/middleware/rbac.py
"""
Tier-based RBAC (Role-Based Access Control) for AI Prompt System

Provides fine-grained access control based on:
- User roles (admin, developer, user)
- Tier access (core, universal, mpv_stage, projects)
- Permission checks
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"


class Tier(str, Enum):
    """Prompt tiers."""
    CORE = "core"
    UNIVERSAL = "universal"
    MPV_STAGE = "mpv_stage"
    PROJECTS = "projects"


class Permission(str, Enum):
    """Available permissions."""
    READ_PROMPTS = "read_prompts"
    RUN_PROMPT = "run_prompt"
    WRITE_PROMPTS = "write_prompts"
    DELETE_PROMPTS = "delete_prompts"
    MANAGE_PROJECTS = "manage_projects"
    MANAGE_PACKS = "manage_packs"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_PROMPTS,
        Permission.RUN_PROMPT,
        Permission.WRITE_PROMPTS,
        Permission.DELETE_PROMPTS,
        Permission.MANAGE_PROJECTS,
        Permission.MANAGE_PACKS,
        Permission.ADMIN,
    ],
    Role.DEVELOPER: [
        Permission.READ_PROMPTS,
        Permission.RUN_PROMPT,
        Permission.WRITE_PROMPTS,
    ],
    Role.USER: [
        Permission.READ_PROMPTS,
        Permission.RUN_PROMPT,
    ],
    Role.GUEST: [
        Permission.READ_PROMPTS,
    ],
}


# Role to tier access mapping
ROLE_TIER_ACCESS = {
    Role.ADMIN: [Tier.CORE, Tier.UNIVERSAL, Tier.MPV_STAGE, Tier.PROJECTS],
    Role.DEVELOPER: [Tier.UNIVERSAL, Tier.MPV_STAGE, Tier.PROJECTS],
    Role.USER: [Tier.UNIVERSAL],
    Role.GUEST: [Tier.UNIVERSAL],
}


@dataclass
class AccessContext:
    """Access control context."""
    user_id: str
    role: Role
    project_id: Optional[str] = None


class RBACService:
    """Role-Based Access Control service."""

    def __init__(self):
        self._custom_roles: Dict[str, Dict] = {}

    def get_role_permissions(self, role: Role) -> List[Permission]:
        """Get permissions for a role."""
        return ROLE_PERMISSIONS.get(role, [])

    def get_role_tier_access(self, role: Role) -> List[Tier]:
        """Get tier access for a role."""
        return ROLE_TIER_ACCESS.get(role, [])

    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if role has permission."""
        permissions = self.get_role_permissions(role)
        return permission in permissions or Permission.ADMIN in permissions

    def has_tier_access(self, role: Role, tier: Tier) -> bool:
        """Check if role has access to tier."""
        tier_access = self.get_role_tier_access(role)
        return tier in tier_access

    def can_access_prompt(
        self,
        role: Role,
        tier: Tier,
        project_id: Optional[str] = None
    ) -> bool:
        """Check if role can access prompt in tier."""
        if not self.has_tier_access(role, tier):
            return False

        # For projects tier, also check project ownership
        if tier == Tier.PROJECTS and project_id:
            # In production, check project membership
            return True

        return True

    def validate_access(
        self,
        context: AccessContext,
        permission: Permission = None,
        tier: Tier = None,
        project_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate access request.
        Returns (allowed, reason_if_not)
        """
        # Check permission
        if permission and not self.has_permission(context.role, permission):
            return False, f"Role {context.role.value} lacks {permission.value}"

        # Check tier access
        if tier and not self.has_tier_access(context.role, tier):
            return False, f"Role {context.role.value} cannot access {tier.value} tier"

        # Check prompt access
        if tier and not self.can_access_prompt(context.role, tier, project_id):
            return False, f"Cannot access {tier.value} for project {project_id}"

        return True, None

    def register_custom_role(
        self,
        name: str,
        permissions: List[Permission],
        tier_access: List[Tier]
    ):
        """Register a custom role."""
        self._custom_roles[name] = {
            "permissions": permissions,
            "tier_access": tier_access
        }
        logger.info(f"Registered custom role: {name}")


# Global RBAC service
_rbac_service: Optional[RBACService] = None


def get_rbac_service() -> RBACService:
    """Get or create global RBAC service."""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service
