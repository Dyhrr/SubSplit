import os
import json
from datetime import datetime

# Define defaults
DEFAULT_CONFIG = {
    "model": "large",
    "max_threads": 2,
    "output_dir": "",
    "watch_folder": False,
    "watch_path": "",
    "openai_api_key": ""
}

CONFIG_FILE = 'config.json'

def get_config():
    """
    Load the configuration from CONFIG_FILE, validate it against DEFAULT_CONFIG,
    fill in any missing or invalid entries, and return a dict.
    If the file is missing or corrupted, back it up and create a new one.
    """
    # If no config file, write defaults
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    # Try to load existing config
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
    except (json.JSONDecodeError, IOError):
        # Backup the corrupt file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bad_name = f"{CONFIG_FILE}.bad.{timestamp}"
        os.rename(CONFIG_FILE, bad_name)
        # Write a fresh default config
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    # Validate keys and types
    updated = False
    for key, default_val in DEFAULT_CONFIG.items():
        if key not in cfg or not isinstance(cfg[key], type(default_val)):
            cfg[key] = default_val
            updated = True

    # Clean out any unexpected keys
    extra_keys = set(cfg.keys()) - set(DEFAULT_CONFIG.keys())
    if extra_keys:
        for key in extra_keys:
            cfg.pop(key)
        updated = True

    # If we fixed anything, persist changes
    if updated:
        save_config(cfg)

    return cfg

def save_config(cfg):
    """
    Save the configuration dictionary to CONFIG_FILE in JSON format.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(cfg, f, indent=4)
    except IOError as e:
        raise RuntimeError(f"Unable to write config file: {e}")