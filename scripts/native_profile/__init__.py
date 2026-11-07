"""Small SVG sections for the native GitHub profile."""
from . import hero, projects, shipped, activity, analytics, details, readme


def render(data, asset_ref='main'):
    for section in (hero, projects, shipped, activity, analytics, details):
        section.render(data)
    readme.render(data, asset_ref)
