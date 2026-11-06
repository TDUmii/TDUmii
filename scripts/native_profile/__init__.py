"""Small SVG sections for the native GitHub profile."""
from . import hero, projects, activity, details, readme


def render(data):
    for section in (hero, projects, activity, details, readme):
        section.render(data)
