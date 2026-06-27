from pathlib import Path
import json

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "issues.json"
USERS_FILE = DATA_DIR / "users.json"
USERS_EXAMPLE_FILE = DATA_DIR / "users.example.json"


def load_data():
    """Load issues from the JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
    return []


def save_data(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_users() -> dict:
    """Load users from the JSON file."""
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
    return {}
