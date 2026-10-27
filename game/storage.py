"""Save/load progress as JSON. Missing or corrupted files never crash the game."""
import json
from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parent.parent / "saves" / "progress.json"


def save_progress(mission, path=SAVE_FILE):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(mission.to_dict(), f, indent=2)
        return True
    except OSError:
        return False  # saving is optional; the game keeps running


def load_saved_dict(path=SAVE_FILE):
    """Return the saved dict, or None if there is no usable save."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        return saved if isinstance(saved, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def has_save(path=SAVE_FILE):
    return load_saved_dict(path) is not None


def clear_save(path=SAVE_FILE):
    try:
        path.unlink()
    except OSError:
        pass
