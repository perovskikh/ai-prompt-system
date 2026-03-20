#!/usr/bin/env python3
"""
Simple standalone server for testing AI Prompt System without fastmcp dependency.

This provides a simple HTTP API to test the core functionality:
- Load prompts
- List prompts
- Search prompts
- Baseline verification
"""

import sys
import json
import hashlib
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging
import asyncio
from datetime import datetime
from functools import lru_cache

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import our storage (may fail if pydantic not available)
try:
    from src.storage.prompts_v2 import (
        PromptStorageV2,
        PromptTier,
        Prompt,
        PromptNotFoundError,
        BaselineIntegrityError
    )
    USE_V2_STORAGE = True
except ImportError:
    USE_V2_STORAGE = False
    logging.warning("Using fallback storage (v2 storage not available)")
    from src.storage.prompts import PromptStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global storage instance
storage = None


def get_storage():
    """Get or create global storage instance."""
    global storage
    if storage is None:
        if USE_V2_STORAGE:
            storage = PromptStorageV2()
        else:
            storage = PromptStorage()
    return storage


class PromptAPIHandler(SimpleHTTPRequestHandler):
    """Simple HTTP request handler for prompt operations."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse path
            parsed_path = urlparse(self.path).path
            logger.info(f"GET {parsed_path}")

            if parsed_path == "/" or parsed_path == "":
                self.send_json_response({
                    "server": "AI Prompt System",
                    "version": "2.0.0",
                    "status": "running",
                    "available_endpoints": [
                        "/prompts",
                        "/prompts/{name}",
                        "/search",
                        "/verify-baseline",
                        "/health"
                    ]
                })
            elif parsed_path == "/health":
                self.send_json_response({
                    "status": "healthy",
                    "storage": USE_V2_STORAGE and "v2" or "legacy",
                    "timestamp": datetime.now().isoformat()
                })
            elif parsed_path == "/prompts":
                prompts = self.list_all_prompts()
                self.send_json_response(prompts)
            elif parsed_path.startswith("/prompts/"):
                prompt_name = parsed_path[9:].replace("/", "")
                if prompt_name:
                    prompt = self.load_prompt(prompt_name)
                    self.send_json_response(prompt)
                else:
                    self.send_custom_error("Prompt name required", 400)
            elif parsed_path == "/search":
                # Get query from URL parameters
                query = parse_qs(urlparse(self.path).query).get('q', [''])[0]
                if query:
                    prompts = self.search_prompts(query)
                else:
                    prompts = self.list_all_prompts()
                self.send_json_response(prompts)
            elif parsed_path == "/verify-baseline":
                results = self.verify_baseline()
                self.send_json_response(results)
            else:
                self.send_custom_error("Not found", 404)

        except Exception as e:
            logger.error(f"Error in GET {parsed_path}: {e}")
            self.send_custom_error("Internal server error", 500)

    def list_all_prompts(self):
        """List all available prompts."""
        try:
            storage = get_storage()
            prompts = storage.list_prompts()

            return {
                "status": "success",
                "count": len(prompts),
                "storage": USE_V2_STORAGE and "v2" or "legacy",
                "prompts": prompts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return {"status": "error", "error": str(e)}

    def load_prompt(self, name):
        """Load a specific prompt by name."""
        try:
            storage = get_storage()
            prompt = storage.load_prompt(name)

            return {
                "status": "success",
                "name": prompt.name,
                "content": prompt.content,
                "version": prompt.version,
                "tier": prompt.tier.value if USE_V2_STORAGE else "unknown",
                "immutable": prompt.immutable,
                "overridable": prompt.overridable,
                "tags": prompt.tags,
                "checksum": prompt.checksum,
                "timestamp": datetime.now().isoformat()
            }
        except PromptNotFoundError as e:
            logger.error(f"Prompt not found: {name}")
            return {"status": "error", "error": str(e)}
        except Exception as e:
            logger.error(f"Error loading prompt {name}: {e}")
            return {"status": "error", "error": str(e)}

    def search_prompts(self, query):
        """Search prompts by query string."""
        try:
            storage = get_storage()
            prompts = storage.search_prompts(query) if query else storage.list_prompts()

            return {
                "status": "success",
                "query": query,
                "count": len(prompts),
                "results": prompts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error searching prompts: {e}")
            return {"status": "error", "error": str(e)}

    def verify_baseline(self):
        """Verify baseline integrity."""
        try:
            storage = get_storage()
            results = storage.verify_baseline_integrity()

            return {
                "status": "success",
                "verified": results.get("verified", False),
                "verified_count": len(results.get("verified_prompts", [])),
                "failed_count": len(results.get("failed_prompts", [])),
                "missing_count": len(results.get("missing_prompts", [])),
                "details": results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error verifying baseline: {e}")
            return {"status": "error", "error": str(e)}

    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def send_custom_error(self, message, status_code=400):
        """Send error response."""
        self.send_error_json(message, status_code)

    def send_error_json(self, message, status_code=400):
        """Send error response as JSON."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "error": message
        }).encode())


def run_server(host="0.0.0", port=8000):
    """Run the HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PromptAPIHandler)

    logger.info(f"Starting AI Prompt System Server on http://{host}:{port}")
    logger.info(f"Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    finally:
        httpd.server_close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Prompt System Server")
    parser.add_argument("--host", default="0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")

    args = parser.parse_args()

    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
