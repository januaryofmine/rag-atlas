from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_config(filename: str) -> Any:
    """Read one Phase-1 JSON definition from the packaged `config/` folder."""
    raw = files("config").joinpath(filename).read_text(encoding="utf-8")
    return json.loads(raw)
