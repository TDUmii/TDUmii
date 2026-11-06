"""CLI and import entry point for the GitHub-native profile."""
import json
import argparse
from native_profile import render
from native_profile.core import ASSETS


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset-ref', default='main', help='Commit containing the generated assets; pins native images against stale branch caches.')
    args = parser.parse_args()
    render(json.loads((ASSETS / "profile-data.json").read_text()), args.asset_ref)
