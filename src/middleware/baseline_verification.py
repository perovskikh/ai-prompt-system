# src/middleware/baseline_verification.py
"""
Baseline verification middleware for AI Prompt System.

Provides middleware hooks for verifying core prompt integrity
on every request or based on configuration.
"""

from typing import Callable, Optional, Dict, Any
from functools import wraps
import logging
from fastapi import Request, Response, HTTPException, status

logger = logging.getLogger(__name__)


class BaselineVerificationError(Exception):
    """Raised when baseline verification fails."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class BaselineVerificationConfig:
    """Configuration for baseline verification middleware."""

    def __init__(
        self,
        enabled: bool = True,
        verify_on_startup: bool = True,
        verify_on_load: bool = True,
        verify_interval_seconds: int = 3600,
        action_on_mismatch: str = "log_warning",  # log_warning or raise_error
        allow_dev_override: bool = True
    ):
        self.enabled = enabled
        self.verify_on_startup = verify_on_startup
        self.verify_on_load = verify_on_load
        self.verify_interval_seconds = verify_interval_seconds
        self.action_on_mismatch = action_on_mismatch
        self.allow_dev_override = allow_dev_override
        self._last_verification = 0

    def should_verify_now(self) -> bool:
        """Check if verification should run based on interval."""
        import time
        now = time.time()
        return (now - self._last_verification) >= self.verify_interval_seconds

    def mark_verification_done(self):
        """Mark that verification has been performed."""
        import time
        self._last_verification = time.time()


# Global configuration instance
verification_config = BaselineVerificationConfig()


def verify_baseline_on_startup(storage) -> Dict:
    """
    Verify baseline integrity on application startup.

    Args:
        storage: PromptStorageV2 instance

    Returns:
        dict: Verification results
    """
    if not verification_config.enabled:
        logger.info("Baseline verification disabled")
        return {"verified": True, "skipped": True}

    logger.info("Verifying baseline integrity on startup...")

    try:
        results = storage.verify_baseline_integrity()

        if results["verified"]:
            logger.info("✅ Baseline verification passed")
        else:
            if verification_config.action_on_mismatch == "raise_error":
                raise BaselineVerificationError(
                    "Baseline integrity check failed",
                    details=results
                )
            else:
                logger.warning(
                    "⚠️  Baseline verification warnings:\n"
                    f"  Failed: {len(results['failed_prompts'])}\n"
                    f"  Missing: {len(results['missing_prompts'])}"
                )

        verification_config.mark_verification_done()
        return results

    except Exception as e:
        logger.error(f"Baseline verification error: {e}")
        if verification_config.action_on_mismatch == "raise_error":
            raise
        return {"verified": False, "error": str(e)}


async def baseline_verification_middleware(
    request: Request,
    call_next: Callable,
    config: Optional[BaselineVerificationConfig] = None
) -> Response:
    """
    ASGI middleware for baseline verification.

    This middleware can be used with FastAPI to verify baseline
    integrity periodically or on specific requests.

    Args:
        request: FastAPI request
        call_next: Next middleware/route handler
        config: Optional verification config (uses global if not provided)

    Returns:
        Response: HTTP response
    """
    # Use provided config or global
    cfg = config or verification_config

    # Skip verification if disabled
    if not cfg.enabled:
        return await call_next(request)

    # Check if verification is needed based on interval
    if not cfg.should_verify_now():
        return await call_next(request)

    # Perform verification (async wrapper)
    try:
        from src.storage.prompts_v2 import get_storage
        storage = get_storage()

        if cfg.verify_on_load:
            results = storage.verify_baseline_integrity()
            cfg.mark_verification_done()

            if not results["verified"] and cfg.action_on_mismatch == "raise_error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Baseline integrity check failed",
                        "details": results
                    }
                )

        return await call_next(request)

    except BaselineVerificationError as e:
        logger.error(f"Baseline verification error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in baseline verification: {e}")
        # Continue even if verification fails
        return await call_next(request)


def verify_baseline_decorator(
    enabled: bool = True,
    on_error: str = "log_warning"  # log_warning, raise_error, or ignore
):
    """
    Decorator to verify baseline integrity before executing a function.

    Usage:
        @verify_baseline_decorator(enabled=True)
        async def load_and_execute_prompt(prompt_name: str):
            # Function will verify baseline before executing
            pass

    Args:
        enabled: Whether to enable verification
        on_error: Action to take on verification failure

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not enabled or not verification_config.enabled:
                return await func(*args, **kwargs)

            try:
                from src.storage.prompts_v2 import get_storage
                storage = get_storage()

                if verification_config.verify_on_load:
                    results = storage.verify_baseline_integrity()

                    if not results["verified"]:
                        if on_error == "raise_error":
                            raise BaselineVerificationError(
                                "Baseline integrity check failed",
                                details=results
                            )
                        elif on_error == "log_warning":
                            logger.warning(
                                f"⚠️  Baseline verification failed: {results}"
                            )
                        # If on_error == "ignore", continue without raising

                return await func(*args, **kwargs)

            except BaselineVerificationError as e:
                logger.error(f"Baseline verification error: {e.message}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in baseline verification: {e}")
                # Continue even if verification fails
                return await func(*args, **kwargs)

        return wrapper
    return decorator


def configure_baseline_verification(
    enabled: bool = True,
    verify_on_startup: bool = True,
    verify_on_load: bool = True,
    verify_interval_seconds: int = 3600,
    action_on_mismatch: str = "log_warning",
    allow_dev_override: bool = True
):
    """
    Configure global baseline verification settings.

    Args:
        enabled: Enable/disable baseline verification
        verify_on_startup: Verify on application startup
        verify_on_load: Verify on every prompt load
        verify_interval_seconds: Interval between verifications
        action_on_mismatch: Action on mismatch (log_warning or raise_error)
        allow_dev_override: Allow override in development
    """
    global verification_config
    verification_config = BaselineVerificationConfig(
        enabled=enabled,
        verify_on_startup=verify_on_startup,
        verify_on_load=verify_on_load,
        verify_interval_seconds=verify_interval_seconds,
        action_on_mismatch=action_on_mismatch,
        allow_dev_override=allow_dev_override
    )
    logger.info(
        f"Baseline verification configured: enabled={enabled}, "
        f"verify_on_startup={verify_on_startup}, "
        f"verify_on_load={verify_on_load}, "
        f"action_on_mismatch={action_on_mismatch}"
    )
