"""vendors.yaml loader and per-action schema validator.

The validator is a mechanical gatekeeper: a malformed vendor profile is
rejected with a precise ``ConfigurationError`` *before* any filesystem
operation runs (see docs/TASK.md Issue I1.4).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from installer.errors import ConfigurationError

#: Valid values for a vendor profile's ``bootstrap_strategy``.
_STRATEGIES = ("at_import", "marker_block", "none")

#: Actions that copy/link framework content and therefore require a ``source``.
_SOURCED_ACTIONS = ("link_per_item", "link_folder", "copy")

#: Every recognized component action.
_ACTIONS = _SOURCED_ACTIONS + ("mkdir",)


def load_vendors(path: Path) -> dict:
    """Parse ``vendors.yaml`` into a dict.

    Raises:
        ConfigurationError: the file is missing, not valid YAML, not a
            top-level mapping, or lacks a ``version`` / non-empty ``vendors`` key.
    """
    path = Path(path)
    if not path.is_file():
        raise ConfigurationError(f"vendors.yaml not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigurationError(f"cannot read vendors.yaml ({path}): {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"vendors.yaml is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError("vendors.yaml must be a mapping at the top level")
    if "version" not in data:
        raise ConfigurationError("vendors.yaml missing required key: 'version'")
    vendors = data.get("vendors")
    if not isinstance(vendors, dict) or not vendors:
        raise ConfigurationError(
            "vendors.yaml missing required key: 'vendors' (a non-empty mapping)"
        )
    return data


def validate_component(component: dict, framework_root: Path, context: str = "") -> None:
    """Validate one component-action spec against the per-action schema.

    ``link_per_item`` / ``link_folder`` / ``copy`` require a ``source`` that
    resolves inside ``framework_root`` (unless the component is ``optional``).
    ``mkdir`` must NOT carry a ``source``. ``path`` is always required.

    Raises:
        ConfigurationError: naming the offending field.
    """
    where = f"{context}: " if context else ""
    if not isinstance(component, dict):
        raise ConfigurationError(
            f"{where}component must be a mapping, got {type(component).__name__}"
        )
    path = component.get("path")
    if not path or not isinstance(path, str):
        raise ConfigurationError(f"{where}component is missing a non-empty string 'path'")
    action = component.get("action")
    if action not in _ACTIONS:
        raise ConfigurationError(
            f"{where}component '{path}' has invalid action {action!r}; "
            f"expected one of {list(_ACTIONS)}"
        )
    source = component.get("source")
    if action == "mkdir":
        if source is not None:
            raise ConfigurationError(
                f"{where}component '{path}' uses action 'mkdir' and must not declare a 'source'"
            )
        return
    # Sourced action (link_per_item / link_folder / copy).
    if not source or not isinstance(source, str):
        raise ConfigurationError(
            f"{where}component '{path}' uses action '{action}' and requires a string 'source'"
        )
    if component.get("optional"):
        return  # An optional component's source may legitimately be absent.
    resolved = Path(framework_root) / source
    if not resolved.exists():
        raise ConfigurationError(
            f"{where}component '{path}' source '{source}' does not exist in the "
            f"framework ({resolved})"
        )


def validate_profile(name: str, profile: dict, framework_root: Path) -> None:
    """Validate a single vendor profile against the schema.

    Checks the ``bootstrap_strategy`` enum, the ``marker_block ⇒
    bootstrap_source`` rule, ``bootstrap_aliases`` / ``git_root_required``
    types, and every entry in ``components``.

    Raises:
        ConfigurationError: naming the offending field.
    """
    if not isinstance(profile, dict):
        raise ConfigurationError(f"vendor '{name}': profile must be a mapping")

    strategy = profile.get("bootstrap_strategy")
    if strategy not in _STRATEGIES:
        raise ConfigurationError(
            f"vendor '{name}': bootstrap_strategy must be one of {list(_STRATEGIES)}, "
            f"got {strategy!r}"
        )
    if strategy == "marker_block":
        source = profile.get("bootstrap_source")
        if not source or not isinstance(source, str):
            raise ConfigurationError(
                f"vendor '{name}': bootstrap_strategy 'marker_block' requires a "
                f"string 'bootstrap_source'"
            )

    bootstrap_file = profile.get("bootstrap_file")
    if bootstrap_file is not None and not isinstance(bootstrap_file, str):
        raise ConfigurationError(
            f"vendor '{name}': bootstrap_file must be a string or null"
        )

    vendor_dir = profile.get("vendor_dir")
    if vendor_dir is not None and not isinstance(vendor_dir, str):
        raise ConfigurationError(
            f"vendor '{name}': vendor_dir must be a string or null"
        )

    aliases = profile.get("bootstrap_aliases", [])
    if not isinstance(aliases, list):
        raise ConfigurationError(f"vendor '{name}': bootstrap_aliases must be a list")

    git_root_required = profile.get("git_root_required", False)
    if not isinstance(git_root_required, bool):
        raise ConfigurationError(
            f"vendor '{name}': git_root_required must be a boolean, got "
            f"{type(git_root_required).__name__}"
        )

    components = profile.get("components", [])
    if not isinstance(components, list):
        raise ConfigurationError(f"vendor '{name}': components must be a list")
    for component in components:
        validate_component(component, framework_root, context=f"vendor '{name}'")


def resolve_profile(vendors: dict, name: str) -> dict:
    """Return ``name``'s profile with ``defaults`` components merged in.

    The resolved ``components`` list is ordered: ``defaults.agent_components``,
    then ``defaults.root_components``, then the vendor's own ``components``.

    Raises:
        ConfigurationError: ``name`` is not a known vendor.
    """
    vendors_map = vendors.get("vendors", {})
    if name not in vendors_map:
        raise ConfigurationError(
            f"unknown vendor {name!r}; known vendors: {sorted(vendors_map)}"
        )
    profile = dict(vendors_map[name])  # shallow copy — do not mutate the source
    defaults = vendors.get("defaults", {}) or {}
    merged: list = []
    merged.extend(defaults.get("agent_components", []) or [])
    merged.extend(defaults.get("root_components", []) or [])
    merged.extend(profile.get("components", []) or [])
    profile["components"] = merged
    return profile
