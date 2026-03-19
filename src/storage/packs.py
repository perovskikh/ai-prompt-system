# src/storage/packs.py
"""
Plugin Pack Loader for AI Prompt System v2.0.0

Manages domain-specific plugin packs:
- k8s-pack: Kubernetes operations
- ci-cd-pack: CI/CD pipelines
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
import json
import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class PackManifest(BaseModel):
    """Plugin pack manifest model."""
    name: str
    version: str
    description: str = ""
    tier: int = 3
    author: str = "AI Prompt System"
    mcp_requires: List[str] = []
    prompts: List[str] = []
    triggers: Dict[str, str] = {}
    dependencies: List[str] = []
    tags: List[str] = []
    created_at: str = ""


class PackNotFoundError(Exception):
    """Raised when a pack is not found."""
    pass


class PackLoader:
    """Loads and manages plugin packs."""

    def __init__(self, packs_dir: str = "./prompts/packs"):
        self.packs_dir = Path(packs_dir)
        self._packs: Dict[str, PackManifest] = {}
        self._load_all_packs()

    def _load_all_packs(self):
        """Load all packs from the packs directory."""
        if not self.packs_dir.exists():
            logger.warning(f"Packs directory not found: {self.packs_dir}")
            return

        for item in self.packs_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                pack_file = item / "pack.json"
                if pack_file.exists():
                    try:
                        with open(pack_file, 'r') as f:
                            data = json.load(f)
                        manifest = PackManifest(**data)
                        self._packs[manifest.name] = manifest
                        logger.info(f"Loaded pack: {manifest.name} v{manifest.version}")
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.error(f"Invalid pack manifest {pack_file}: {e}")

    def list_packs(self) -> List[Dict[str, Any]]:
        """List all available packs."""
        return [
            {
                "name": pack.name,
                "version": pack.version,
                "description": pack.description,
                "tier": pack.tier,
                "prompt_count": len(pack.prompts),
                "tags": pack.tags
            }
            for pack in self._packs.values()
        ]

    def load_pack(self, name: str) -> PackManifest:
        """Load a specific pack by name."""
        if name not in self._packs:
            raise PackNotFoundError(f"Pack not found: {name}")
        return self._packs[name]

    def find_by_trigger(self, query: str) -> Optional[Dict[str, Any]]:
        """Find a prompt by trigger keyword."""
        query_lower = query.lower()

        for pack in self._packs.values():
            for trigger, prompt_file in pack.triggers.items():
                # Split trigger by comma to handle multiple keywords
                keywords = [k.strip().lower() for k in trigger.split(',')]
                for keyword in keywords:
                    if keyword and keyword in query_lower:
                        return {
                            "pack": pack.name,
                            "prompt_file": prompt_file,
                            "trigger": trigger,
                            "matched_keyword": keyword
                        }
        return None

    def get_prompts_for_pack(self, pack_name: str) -> List[str]:
        """Get all prompt files for a specific pack."""
        pack = self.load_pack(pack_name)
        pack_dir = self.packs_dir / pack_name
        return [
            str(pack_dir / p)
            for p in pack.prompts
            if (pack_dir / p).exists()
        ]

    def get_all_triggers(self) -> Dict[str, str]:
        """Get all triggers mapped to pack.prompt_file."""
        triggers = {}
        for pack in self._packs.values():
            for trigger, prompt_file in pack.triggers.items():
                triggers[trigger] = f"{pack.name}:{prompt_file}"
        return triggers


# Global pack loader instance
_pack_loader: Optional[PackLoader] = None


def get_pack_loader() -> PackLoader:
    """Get or create global pack loader instance."""
    global _pack_loader
    if _pack_loader is None:
        _pack_loader = PackLoader()
    return _pack_loader
