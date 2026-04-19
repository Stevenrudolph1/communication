"""config.py — Load XaviMail config from ~/.xavimail/config.json"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / '.xavimail' / 'config.json'

def load() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f'XaviMail config not found at {CONFIG_PATH}. Run setup first.')
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    # Expand ~ in paths
    for key in ('db_path', 'contacts_json'):
        if key in cfg:
            cfg[key] = str(Path(cfg[key]).expanduser())
    return cfg
