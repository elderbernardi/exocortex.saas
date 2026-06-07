#!/usr/bin/env python3
"""Google Cloud quick-setup guide generator with deep links.

Detects existing GCP project configuration and generates pre-filled
deep links for the Google Cloud Console, reducing the manual OAuth
setup from 9 clicks to the minimum necessary.

Usage:
    gcloud_quick_setup.py                        # Auto-detect project
    gcloud_quick_setup.py --project 734420556052  # Force project ID
    gcloud_quick_setup.py --check-apis            # Test which APIs are enabled

Output: JSON with project_id, detected_from, setup_url, api_links, credentials_url, test_users_url
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ensure sibling modules are importable
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _hermes_home import get_hermes_home

HERMES_HOME = get_hermes_home()
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"

# APIs required for full Google Workspace access
REQUIRED_APIS = [
    ("Gmail API", "gmail.googleapis.com"),
    ("Google Calendar API", "calendar-json.googleapis.com"),
    ("Google Drive API", "drive.googleapis.com"),
    ("Google Sheets API", "sheets.googleapis.com"),
    ("Google Docs API", "docs.googleapis.com"),
    ("People API", "people.googleapis.com"),
]

# Console base URLs
CONSOLE_BASE = "https://console.cloud.google.com"
API_LIBRARY_BASE = f"{CONSOLE_BASE}/apis/library"
CREDENTIALS_URL = f"{CONSOLE_BASE}/apis/credentials"
TEST_USERS_URL = f"{CONSOLE_BASE}/auth/audience"
PROJECT_SELECTOR_URL = f"{CONSOLE_BASE}/projectselector2/home/dashboard"


def detect_project_id() -> tuple[str | None, str]:
    """Try to find a GCP project ID. Returns (project_id, source)."""
    # 1. From existing client_secret.json
    if CLIENT_SECRET_PATH.exists():
        try:
            data = json.loads(CLIENT_SECRET_PATH.read_text())
            # Desktop/installed app format
            installed = data.get("installed") or data.get("web", {})
            client_id = installed.get("client_id", "")
            # Project number is the prefix before the first '-'
            if "-" in client_id:
                project_part = client_id.split("-")[0]
                if project_part.isdigit():
                    return project_part, "client_secret.json"
        except Exception:
            pass

    # 2. From gcloud CLI
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "gcloud config"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. From default project in gcloud
    try:
        result = subprocess.run(
            ["gcloud", "projects", "list", "--format=value(projectId)", "--limit=1"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "gcloud projects list"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None, "not_found"


def generate_api_links(project_id: str) -> list[dict]:
    """Generate deep links for each required API."""
    links = []
    for name, api_id in REQUIRED_APIS:
        url = f"{API_LIBRARY_BASE}/{api_id}?project={project_id}"
        links.append({"name": name, "api_id": api_id, "enable_url": url})
    return links


def generate_enable_all_url(project_id: str) -> str:
    """Generate a single URL that opens the API Library for the project."""
    return f"{API_LIBRARY_BASE}?project={project_id}"


def generate_credentials_url(project_id: str) -> str:
    """Generate URL to create OAuth client."""
    return f"{CREDENTIALS_URL}?project={project_id}"


def generate_test_users_url(project_id: str) -> str:
    """Generate URL to add test users."""
    return f"{TEST_USERS_URL}?project={project_id}"


def generate_setup_url(project_id: str) -> str:
    """Generate the main project dashboard URL."""
    return f"{CONSOLE_BASE}/home/dashboard?project={project_id}"


def check_apis_enabled(project_id: str) -> list[dict]:
    """Check which APIs are enabled for the project using gcloud."""
    results = []
    for name, api_id in REQUIRED_APIS:
        try:
            result = subprocess.run(
                ["gcloud", "services", "list", "--enabled",
                 f"--filter=config.name:{api_id}",
                 f"--project={project_id}",
                 "--format=value(config.name)"],
                capture_output=True, text=True, timeout=30,
            )
            enabled = api_id in result.stdout
            results.append({"name": name, "api_id": api_id, "enabled": enabled})
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results.append({"name": name, "api_id": api_id, "enabled": None, "error": "gcloud not available"})
    return results


def main():
    parser = argparse.ArgumentParser(description="Google Cloud quick-setup guide generator")
    parser.add_argument("--project", metavar="ID", help="Force GCP project ID (skip detection)")
    parser.add_argument("--check-apis", action="store_true", help="Check which APIs are enabled (requires gcloud)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    # Detect or use provided project ID
    if args.project:
        project_id = args.project
        detected_from = "user_provided"
    else:
        project_id, detected_from = detect_project_id()

    if not project_id:
        print(json.dumps({
            "error": "no_project_detected",
            "message": "Could not detect GCP project. Provide one with --project or create one at:",
            "project_selector_url": PROJECT_SELECTOR_URL,
        }, indent=2))
        sys.exit(1)

    # Build result
    result = {
        "project_id": project_id,
        "detected_from": detected_from,
        "has_client_secret": CLIENT_SECRET_PATH.exists(),
        "setup_url": generate_setup_url(project_id),
        "api_links": generate_api_links(project_id),
        "enable_all_url": generate_enable_all_url(project_id),
        "credentials_url": generate_credentials_url(project_id),
        "test_users_url": generate_test_users_url(project_id),
        "project_selector_url": PROJECT_SELECTOR_URL,
    }

    # Optional: check APIs
    if args.check_apis:
        result["api_status"] = check_apis_enabled(project_id)
        result["all_enabled"] = all(
            a.get("enabled") is True for a in result["api_status"]
        )

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Project: {project_id} (from {detected_from})")
        print(f"Client secret: {'found' if result['has_client_secret'] else 'missing'}")
        print(f"\nSetup: {result['setup_url']}")
        print(f"\nAPIs to enable:")
        for link in result["api_links"]:
            print(f"  {link['name']}: {link['enable_url']}")
        print(f"\nCreate OAuth client: {result['credentials_url']}")
        print(f"Add test users: {result['test_users_url']}")
        if args.check_apis:
            print(f"\nAPI status:")
            for api in result["api_status"]:
                status = "✅" if api.get("enabled") else ("❌" if api.get("enabled") is False else "❓")
                print(f"  {status} {api['name']}")


if __name__ == "__main__":
    main()
