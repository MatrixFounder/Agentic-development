"""Application configuration: YAML file + environment variable overlay.

Precedence (highest wins): environment variables > config file > defaults.
"""

import logging
import os
from typing import Any, Optional

import yaml

logger = logging.getLogger("config")

DEFAULTS: dict[str, Any] = {
    "db_url": "sqlite:///app.db",
    "log_level": "INFO",
    "worker_count": 4,
    "feature_flags": {},
    "request_timeout_s": 30,
}

ENV_PREFIX = "APP_"


class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def _read_file(self) -> dict[str, Any]:
        if not os.path.exists(self.config_path):
            logger.warning("config file missing: %s", self.config_path)
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
        if not isinstance(data, dict):
            logger.error("config root must be a mapping, got %s", type(data))
            return {}
        return data

    def _read_env(self) -> dict[str, Any]:
        overlay: dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(ENV_PREFIX):
                continue
            name = key[len(ENV_PREFIX):].lower()
            overlay[name] = self._coerce(value)
        return overlay

    @staticmethod
    def _coerce(raw: str) -> Any:
        lowered = raw.lower()
        if lowered in ("true", "false"):
            return lowered == "true"
        try:
            return int(raw)
        except ValueError:
            pass
        try:
            return float(raw)
        except ValueError:
            pass
        return raw

    def load(self) -> dict[str, Any]:
        """Merge defaults, file values, and env overrides per module docstring."""
        merged = dict(DEFAULTS)
        merged.update(self._read_env())
        merged.update(self._read_file())
        logger.info("config loaded from %s (%d keys)", self.config_path, len(merged))
        return merged

    def get(self, key: str, fallback: Optional[Any] = None) -> Any:
        """Single-key accessor used by call sites that need one value."""
        config = self.load()
        return config.get(key, fallback)

    def require(self, key: str) -> Any:
        value = self.get(key)
        if value is None:
            raise KeyError(f"missing required config key: {key}")
        return value

    def feature_enabled(self, flag: str) -> bool:
        flags = self.get("feature_flags", {})
        return bool(flags.get(flag, False))
