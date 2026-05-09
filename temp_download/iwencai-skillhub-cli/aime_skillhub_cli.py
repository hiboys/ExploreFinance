#!/usr/bin/env python3
"""AIME Skillhub CLI.

Features:
- Install a skill by slug
"""

import argparse
import os
import sys
import urllib.parse
from pathlib import Path

# Add the cli directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "cli"))

# Import functions from the existing CLI
from cli.skills_store_cli import (
    load_cli_version,
    load_cli_metadata,
    DEFAULT_INDEX_URI_FALLBACK,
    DEFAULT_SEARCH_URL_FALLBACK,
    DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE_FALLBACK,
    DEFAULT_INSTALL_ROOT,
    install_zip_to_target_with_fallback,
    load_lockfile,
    save_lockfile,
    update_clawhub_lock_v1,
    normalize_source_label
)

# Load version and metadata from the existing CLI
CLI_VERSION = load_cli_version(Path(__file__).resolve().parent / "cli")
CLI_METADATA = load_cli_metadata(Path(__file__).resolve().parent / "cli")
DEFAULT_INDEX_URI = CLI_METADATA.get("skills_index_url", DEFAULT_INDEX_URI_FALLBACK)
DEFAULT_SEARCH_URL = os.environ.get("SKILLHUB_SEARCH_URL", "").strip() or CLI_METADATA.get(
    "skills_search_url",
    DEFAULT_SEARCH_URL_FALLBACK,
)
DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE = (
    os.environ.get("SKILLHUB_PRIMARY_DOWNLOAD_URL_TEMPLATE", "").strip()
    or CLI_METADATA.get(
        "skills_primary_download_url_template",
        DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE_FALLBACK,
    )
)

def find_openclaw_workspace():
    """Find OpenClaw workspace directory"""
    import os
    import subprocess
    
    # Try to find openclaw executable
    try:
        # Check if openclaw is in PATH
        subprocess.run(["openclaw", "--version"], capture_output=True, check=True)
        
        # Try to get workspace path from config
        result = subprocess.run(
            ["openclaw", "config", "get", "workspace"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).expanduser().resolve()
        
        # Default workspace path
        return Path("~/.openclaw/workspace").expanduser().resolve()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

def cmd_install(args):
    """Install a skill by slug without index lookup"""
    # Create a skill object with just the slug
    skill = {"slug": args.slug, "name": args.slug, "version": "", "source": "skillhub"}
    print(f'Installing skill: {args.slug}')

    # Generate primary download URL
    encoded_slug = urllib.parse.quote(args.slug)
    primary_zip_url = args.primary_download_url_template.replace("{slug}", encoded_slug)
    if not primary_zip_url:
        print("Error: Primary download URL template resolved empty URL")
        return

    # Determine installation target directory
    install_root = Path(args.dir).expanduser().resolve()
    
    # Check if OpenClaw is installed
    openclaw_workspace = find_openclaw_workspace()
    if openclaw_workspace and openclaw_workspace.exists():
        install_root = openclaw_workspace / "skills"
        print(f"OpenClaw detected, installing to: {install_root}")
    
    target_dir = install_root / args.slug
    expected_sha256 = ""  # No SHA256 verification

    # Install the skill
    try:
        install_zip_to_target_with_fallback(
            slug=args.slug,
            zip_uris=[primary_zip_url],
            target_dir=target_dir,
            force=args.force,
            expected_sha256=expected_sha256,
        )

        # Update lock files
        lock = load_lockfile(install_root)
        skills_lock = lock.setdefault("skills", {})
        skills_lock[args.slug] = {
            "name": skill.get("name", args.slug),
            "zip_url": primary_zip_url,
            "source": normalize_source_label(skill.get("source")),
            "version": str(skill.get("version", "")).strip(),
        }
        save_lockfile(install_root, lock)
        update_clawhub_lock_v1(args.slug, str(skill.get("version", "")).strip())
        print(f"Installed: {args.slug} -> {target_dir}")
    except Exception as e:
        print(f"Error: {e}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AIME Skillhub CLI")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"aime-skillhub-cli {CLI_VERSION}",
        help="Show AIME Skillhub CLI version and exit",
    )
    parser.add_argument(
        "--dir",
        default=DEFAULT_INSTALL_ROOT,
        help='Install root directory (default: "./skills")',
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="Install a skill by slug")
    install.add_argument("slug", help="Skill slug")
    install.add_argument(
        "--primary-download-url-template",
        default=DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE,
        help=(
            "Primary download URL template for install (supports {slug}). "
            "This is the only remote source used by install."
        ),
    )
    install.add_argument("--force", action="store_true", help="Overwrite existing target directory")
    install.set_defaults(func=cmd_install)

    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
