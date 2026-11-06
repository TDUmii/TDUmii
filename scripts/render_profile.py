"""CLI and import entry point for the GitHub-native profile."""
import json
from native_profile import render
from native_profile.core import ASSETS


if __name__ == "__main__":
    render(json.loads((ASSETS / "profile-data.json").read_text()))
