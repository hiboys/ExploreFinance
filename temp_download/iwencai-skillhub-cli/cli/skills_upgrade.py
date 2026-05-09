#!/usr/bin/env python3
"""Skill upgrade flow extracted from the main CLI module."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_non_empty_string(obj: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_update_url(config: Dict[str, Any], skill_dir: Path, resolve_uri_with_base: Callable[[str, Path], str]) -> str:
    direct = _first_non_empty_string(
        config,
        ["update_url", "updateUrl", "upgrade_url", "upgradeUrl", "manifest_url", "manifestUrl"],
    )
    if direct:
        return resolve_uri_with_base(direct, skill_dir)

    for container_key in ("update", "upgrade", "autoupdate"):
        nested = _as_dict(config.get(container_key))
        url_value = _first_non_empty_string(nested, ["url", "uri", "manifest", "manifest_url"])
        if url_value:
            return resolve_uri_with_base(url_value, skill_dir)
    return ""


def _read_installed_skill_version(
    skill_dir: Path,
    lock_meta: Dict[str, Any],
    skill_meta_name: str,
) -> str:
    lock_version = _first_non_empty_string(lock_meta, ["version"])
    if lock_version:
        return lock_version

    meta_path = skill_dir / skill_meta_name
    if meta_path.exists():
        try:
            raw = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                meta_version = _first_non_empty_string(raw, ["version"])
                if meta_version:
                    return meta_version
        except json.JSONDecodeError:
            return ""
    return ""


def cmd_upgrade(args: Any, deps: Dict[str, Any]) -> int:
    load_lockfile = deps["load_lockfile"]
    save_lockfile = deps["save_lockfile"]
    read_json_from_uri = deps["read_json_from_uri"]
    extract_update_manifest_info = deps["extract_update_manifest_info"]
    resolve_uri_with_base = deps["resolve_uri_with_base"]
    version_is_newer = deps["version_is_newer"]
    install_zip_to_target = deps["install_zip_to_target"]
    skill_config_name = deps["skill_config_name"]
    skill_meta_name = deps["skill_meta_name"]

    install_root = Path(args.dir).expanduser().resolve()
    lock = load_lockfile(install_root)
    skills = lock.get("skills", {})
    if not isinstance(skills, dict):
        skills = {}

    if args.slug:
        targets = [args.slug]
    else:
        targets = sorted(skills.keys())
        if not targets:
            raise SystemExit(f"No installed skills in lockfile: {install_root / '.skills_store_lock.json'}")

    checked = 0
    upgraded = 0
    skipped = 0
    failed = 0

    for slug in targets:
        checked += 1
        target_dir = install_root / slug
        if not target_dir.exists():
            print(f"[{slug}] skip: skill directory not found: {target_dir}")
            skipped += 1
            continue

        lock_meta = skills.get(slug)
        lock_meta_dict = lock_meta if isinstance(lock_meta, dict) else {}
        config_path = target_dir / skill_config_name
        if not config_path.exists():
            print(f"[{slug}] skip: {skill_config_name} not found")
            skipped += 1
            continue

        try:
            raw_config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[{slug}] fail: invalid {skill_config_name}: {exc}")
            failed += 1
            continue
        if not isinstance(raw_config, dict):
            print(f"[{slug}] fail: {skill_config_name} must be a JSON object")
            failed += 1
            continue

        update_url = _extract_update_url(raw_config, target_dir, resolve_uri_with_base)
        if not update_url:
            print(f"[{slug}] skip: missing update URL in {skill_config_name}")
            skipped += 1
            continue

        try:
            preserved_config_text = config_path.read_text(encoding="utf-8")
            manifest = read_json_from_uri(update_url, timeout=args.timeout)
            latest_version, package_uri, expected_sha = extract_update_manifest_info(manifest)
            if not latest_version:
                print(f"[{slug}] fail: update manifest missing version: {update_url}")
                failed += 1
                continue
            if not package_uri:
                print(f"[{slug}] fail: update manifest missing package URL: {update_url}")
                failed += 1
                continue

            current_version = _read_installed_skill_version(target_dir, lock_meta_dict, skill_meta_name)
            if not version_is_newer(latest_version, current_version):
                print(f"[{slug}] up-to-date: current={current_version or '<unknown>'} latest={latest_version}")
                skipped += 1
                continue

            package_uri = resolve_uri_with_base(package_uri, target_dir)
            if args.check_only:
                print(
                    f"[{slug}] upgrade available: current={current_version or '<unknown>'} "
                    f"latest={latest_version} package={package_uri}"
                )
                continue

            install_zip_to_target(
                slug=slug,
                zip_uri=package_uri,
                target_dir=target_dir,
                force=True,
                expected_sha256=expected_sha,
            )
            restored_config_path = target_dir / skill_config_name
            if not restored_config_path.exists():
                restored_config_path.write_text(preserved_config_text, encoding="utf-8")

            updated_meta = dict(lock_meta_dict)
            updated_meta["zip_url"] = package_uri
            updated_meta["version"] = latest_version
            updated_meta["update_url"] = update_url
            if not updated_meta.get("name"):
                updated_meta["name"] = slug
            if not updated_meta.get("source"):
                updated_meta["source"] = "unknown"
            skills[slug] = updated_meta
            upgraded += 1
            print(f"[{slug}] upgraded: {current_version or '<unknown>'} -> {latest_version}")
        except SystemExit:
            failed += 1
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"[{slug}] fail: {exc}")
            failed += 1

    lock["skills"] = skills
    save_lockfile(install_root, lock)
    print(
        f"upgrade done: checked={checked} upgraded={upgraded} "
        f"skipped={skipped} failed={failed} dir={install_root}"
    )
    return 2 if failed > 0 else 0
